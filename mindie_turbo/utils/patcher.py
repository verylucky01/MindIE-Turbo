#!/usr/bin/env python
# coding=utf-8
# Copyright (c) Huawei Technologies Co., Ltd. 2025-2025. All rights reserved.
# MindIE is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import importlib
import sys
import types
import re
from typing import Callable, Literal


ALLOWED_MODULE_PREFIXES = ('mindie_turbo.', 'vllm.', 'vllm_ascend.')


def initialize_placeholder(func_name):
    """Create a placeholder function that raises an error when called"""
    def placeholder_function(*args, **kwargs):
        raise RuntimeError(
            f"Function {func_name} requires implementation."
            f"This is not supposed to happen, did you forget to implement the function?"
        )
    return placeholder_function


class Patch:
    """
    A class that handles function/method patching operations.
    Supports both replacement and decoration of existing functions.
    """

    def __init__(
        self,
        target: str,  # Target path in format "module.submodule.function"
        substitute: Callable = None,
        method: Literal["replace", "decorate"] = "replace",
        create: bool = False,  # Whether to create dummy modules if not exist
    ):
        # Validate target format
        self._validate_target_format(target)
        
        self.target_module, self.target_function = target.rsplit(".", 1) if "." in target else (target, None)
        self.original_module = None
        self.original_function = None
        self.candidate: Callable = None
        self.patch_function = None
        self.wrappers = []
        self.applied = False
        self.create = create

        substitute = substitute or initialize_placeholder(target)

        match method:
            case "replace":
                self.set_replacement(substitute)
            case "decorate":
                self.add_decorator(substitute)

    def _validate_target_format(self, target: str) -> None:
        """Validate target path format to prevent malicious inputs."""
        if not target:
            raise ValueError("Target path cannot be empty")
        
        # Validate basic format: alphanumeric, underscore, and dot characters
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', target):
            raise ValueError(f"Invalid target format: {target}. Only alphanumeric, underscore and dot characters are allowed.")
        
        # Prevent relative path traversal
        if any(part in ('', '.', '..') for part in target.split('.')):
            raise ValueError(f"Invalid target path: {target}. Cannot contain empty or relative path components.")
        
        # Limit module creation depth (optional)
        if len(target.split('.')) > 10:  # Reasonable depth limit
            raise ValueError(f"Target path too deep: {target}")

    @property
    def original_function_id(self):
        return id(self.original_function)

    def set_replacement(self, replacement: Callable, force: bool = False):
        """Direct replacement of the target function"""
        if self.candidate and not force:
            raise RuntimeError(
                f"Patch function {self.target_function} is already set, "
                "please use force=True to override the patch function."
            )
        self.candidate = replacement
        self.applied = False

    def add_decorator(self, decorator: Callable):
        """Add a decorator to wrap the target function"""
        self.wrappers.append(decorator)
        self.applied = False

    def apply_patch(self):
        """Apply the patch to the target function and propagate changes to all references"""
        if self.applied:
            return

        self.original_module, self.original_function = Patch.parse_path(
            self.target_module, self.target_function, self.create
        )

        if self.candidate is None:
            self.candidate = self.original_function
        for wrapper in self.wrappers:
            self.candidate = wrapper(self.candidate)
        if self.target_function is not None:
            setattr(self.original_module, self.target_function, self.candidate)

        for key, value in sys.modules.copy().items():
            if (
                self.target_function is not None
                and hasattr(value, self.target_function)
                and id(getattr(value, self.target_function)) == self.original_function_id
            ):
                setattr(value, self.target_function, self.candidate)
        self.applied = True

    @staticmethod
    def parse_path(module_path, function_name, create_dummy):
        """
        Parse module path and resolve/create modules as needed.

        Args:
            module_path: Dot-separated module path
            function_name: Target function name (None for module only)
            create_dummy: Create dummy modules/functions when missing

        Returns:
            Tuple of (resolved module, target function/none)

        Raises:
            ModuleNotFoundError: If module path is invalid and create_dummy=False
            AttributeError: If function is missing and create_dummy=False
        """
        from importlib.machinery import ModuleSpec

        def create_dummy_module(full_path, parent=None):
            """Create and register a placeholder module with security restrictions"""
            # Security restriction: only allow creating modules with specific prefixes
            if not full_path.startswith(ALLOWED_MODULE_PREFIXES):
                raise SecurityError(f"Cannot create dummy module outside allowed prefixes: {full_path}")
            dummy = types.ModuleType(full_path)
            dummy.__file__ = f"<dummy_module>{full_path}.py"  # Explicitly mark as dummy module
            dummy.__spec__ = ModuleSpec(full_path, None)
            dummy.__package__ = full_path
            sys.modules[full_path] = dummy
            
            if parent:
                setattr(parent, full_path.split(".")[-1], dummy)
            return dummy

        def create_placeholder_function(func_name):
            """Create dummy function that raises when called"""
            def placeholder(*args, **kwargs):
                raise NotImplementedError(f"Function {func_name} is a placeholder and should not be called")
            placeholder.__name__ = func_name
            placeholder.__qualname__ = func_name
            return placeholder

        # Validate module path security
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', module_path):
            raise ValueError(f"Invalid module path: {module_path}")

        modules = module_path.split(".")
        current_module = None
        processed_path = []

        for idx, part in enumerate(modules):
            current_path = ".".join(modules[: idx + 1])
            parent_path = ".".join(modules[:idx]) if idx > 0 else None

            try:
                current_module = importlib.import_module(current_path)
            except ModuleNotFoundError:
                # Security restriction: only create dummy modules when explicitly allowed
                if not create_dummy:
                    raise
                
                # Additional security checks
                if any(restricted in current_path for restricted in ['sys', 'os', 'builtins', '__main__']):
                    raise SecurityError(f"Cannot create dummy system module: {current_path}")
                
                if parent_path:
                    try:
                        parent = importlib.import_module(parent_path)
                    except ModuleNotFoundError:
                        raise SecurityError(f"Cannot create module {current_path}: parent {parent_path} not found")
                    
                    current_module = create_dummy_module(current_path, parent)
                else:
                    current_module = create_dummy_module(current_path)

            processed_path.append(part)

        # Final function handling
        final_module = sys.modules[module_path]
        if function_name is not None:
            if not hasattr(final_module, function_name):
                if create_dummy:
                    ph_func = create_placeholder_function(function_name)
                    setattr(final_module, function_name, ph_func)
                else:
                    setattr(final_module, function_name, None)
            return final_module, getattr(final_module, function_name)

        return final_module, None


class SecurityError(Exception):
    """Security-related exception for patch operations"""
    pass


class Patcher:
    """
    Static utility class for managing multiple patches.
    Provides a simplified interface for patch registration and application.
    """

    patches: dict[str, Patch] = {}

    @staticmethod
    def register_patch(
        target: str,
        substitute: Callable = None,
        method: Literal["replace", "decorate"] = "replace",
        create: bool = False,
        force: bool = False,
    ):
        """Register a new patch or update existing one with validation"""
        # Validate target format
        if not target or not isinstance(target, str):
            raise ValueError("Target must be a non-empty string")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', target):
            raise ValueError(f"Invalid target format: {target}")
        
        # Validate method parameter
        if method not in ("replace", "decorate"):
            raise ValueError(f"Method must be 'replace' or 'decorate', got: {method}")
        
        # Validate create parameter
        if not isinstance(create, bool):
            raise ValueError(f"Create must be a boolean, got: {type(create).__name__}")
        
        # Validate force parameter  
        if not isinstance(force, bool):
            raise ValueError(f"Force must be a boolean, got: {type(force).__name__}")

        if target not in Patcher.patches:
            Patcher.patches[target] = Patch(target, substitute, method, create)
        elif method == "replace":
            Patcher.patches.get(target).set_replacement(substitute, force)
        elif method == "decorate":
            Patcher.patches.get(target).add_decorator(substitute)
        else:
            raise ValueError(f"Invalid patch method {method}")

    @staticmethod
    def apply_patches():
        """Apply all registered patches"""
        for patch in Patcher.patches.values():
            try:
                patch.apply_patch()
            except Exception as e:
                # Security consideration: log but continue with other patches
                print(f"Warning: Failed to apply patch {patch.target_module}.{patch.target_function}: {e}")