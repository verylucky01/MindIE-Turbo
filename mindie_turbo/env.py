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

from typing import Any, Callable, Dict, Optional

from mindie_turbo.utils.file_utils import check_file_path


class EnvironmentValidator:
    """
    Environment variable validator for secure and validated access to system environment variables.
    Provides static methods to validate different types of environment variables with proper constraints.
    """
    
    # Constants for validation limits
    MAX_STRING_LENGTH = 4096
    MAX_INT_STRING_LENGTH = 10
    MAX_PATH_LENGTH = 4096
    MAX_ENUM_LENGTH = 20
    
    @staticmethod
    def validate_path(value: Optional[str], path_type: str) -> Optional[str]:
        """
        Validate path environment variables for security and correctness.
        """
        if not value:
            return None
        
        value = check_file_path(value)
        
        return value
    
    @staticmethod
    def validate_boolean(value: Optional[str], var_name: str) -> bool:
        """
        Generic boolean environment variable validation.
        """
        if value is None:
            return False
        
        EnvironmentValidator._validate_string_length(value, 5, var_name)  # "false" is 5 chars
        EnvironmentValidator._validate_boolean_string(value, var_name)
        
        return value.lower() in {"1", "true", "yes"}
    
    @staticmethod
    def validate_integer(value: Optional[str], var_name: str, min_val: int = 0, max_val: int = None) -> Optional[int]:
        """
        Generic integer environment variable validation.
        """
        if value is None:
            return None
        
        EnvironmentValidator._validate_string_length(value, EnvironmentValidator.MAX_INT_STRING_LENGTH, var_name)
        EnvironmentValidator._validate_digits_only(value, var_name)
        
        try:
            num_value = int(value)
            if num_value < min_val:
                raise ValueError(f"{var_name} must be at least {min_val}")
            if max_val is not None and num_value > max_val:
                raise ValueError(f"{var_name} exceeds maximum allowed value ({max_val})")
            return num_value
        except ValueError as e:
            raise ValueError(f"Invalid {var_name} value: {value} - {e}") from e
    
    # Private methods (implementation details)
    @staticmethod
    def _validate_string_length(value: str, max_length: int, var_name: str) -> None:
        """Validate string length."""
        if len(value) > max_length:
            raise ValueError(
                f"{var_name} value too long: {len(value)} characters. "
                f"Maximum allowed: {max_length}"
            )
    
    @staticmethod
    def _validate_not_none(value: Optional[str], var_name: str) -> str:
        """Validate that value is not None and return it."""
        if value is None:
            raise ValueError(f"{var_name} cannot be None")
        return value
    
    @staticmethod
    def _validate_digits_only(value: str, var_name: str) -> None:
        """Validate that string contains only digits."""
        if not value.isdigit():
            raise ValueError(f"{var_name} must contain only digits, got: {value}")
    
    @staticmethod
    def _validate_enum_value(value: str, valid_values: set, var_name: str) -> None:
        """Validate that value is in the set of valid values."""
        if value not in valid_values:
            raise ValueError(
                f"Invalid {var_name}: {value}. "
                f"Must be one of: {', '.join(sorted(valid_values))}"
            )
    
    @staticmethod
    def _validate_boolean_string(value: str, var_name: str) -> None:
        """Validate that value is a valid boolean string."""
        if value not in {"0", "1", "true", "false", "yes", "no"}:
            raise ValueError(
                f"Invalid {var_name} value: {value}. "
                f"Must be one of: '0', '1', 'true', 'false', 'yes', 'no'"
            )


# Dictionary mapping environment variable names to their validation functions
env_variables: Dict[str, Callable[[], Any]] = {}


def __getattr__(name: str):
    """
    Dynamic attribute accessor for environment variables.
    """
    if name in env_variables:
        try:
            return env_variables[name]()
        except ValueError as e:
            raise ValueError(f"Environment variable {name} validation failed: {e}") from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """
    Return list of available environment variable attributes.
    """
    return list(env_variables.keys())
