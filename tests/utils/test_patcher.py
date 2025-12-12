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

import unittest
from unittest.mock import patch, MagicMock
import sys
import types
from mindie_turbo.utils.patcher import Patch, Patcher, SecurityError, initialize_placeholder


class TestPatch(unittest.TestCase):
    """Test Patch class functionality"""

    def setUp(self):
        # Create a test module for testing
        self.test_module = types.ModuleType('test_module')
        self.test_module.test_function = lambda x: x * 2
        sys.modules['test_module'] = self.test_module

    def tearDown(self):
        # Clean up test modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('test_'):
                del sys.modules[mod]

    def test_initialize_placeholder(self):
        """Test placeholder function creation"""
        placeholder = initialize_placeholder('test_func')
        with self.assertRaises(RuntimeError) as context:
            placeholder()
        self.assertIn('test_func', str(context.exception))

    def test_patch_initialization_replace(self):
        """Test Patch initialization with replace method"""
        replacement = lambda x: x * 3
        patch_instance = Patch('test_module.test_function', replacement, 'replace')
        self.assertEqual(patch_instance.target_module, 'test_module')
        self.assertEqual(patch_instance.target_function, 'test_function')
        self.assertEqual(patch_instance.candidate, replacement)

    def test_patch_initialization_decorate(self):
        """Test Patch initialization with decorate method"""
        decorator = lambda func: lambda x: func(x) + 1
        patch_instance = Patch('test_module.test_function', decorator, 'decorate')
        self.assertEqual(len(patch_instance.wrappers), 1)
        self.assertEqual(patch_instance.wrappers[0], decorator)

    def test_patch_initialization_no_substitute(self):
        """Test Patch initialization without substitute"""
        patch_instance = Patch('test_module.test_function')
        self.assertIsNotNone(patch_instance.candidate)
        # Should be a placeholder function
        with self.assertRaises(RuntimeError):
            patch_instance.candidate(5)

    def test_validate_target_format_valid(self):
        """Test target format validation with valid inputs"""
        valid_targets = [
            'module.function',
            'module.submodule.function',
            'valid_name',
            'name_with_underscores',
            'nameWithNumbers123'
        ]
        
        for target in valid_targets:
            try:
                patch_instance = Patch(target, lambda x: x, create=True)
                self.assertEqual(patch_instance.target_module, target.rsplit('.', 1)[0] if '.' in target else target)
            except ValueError:
                self.fail(f"Valid target {target} raised ValueError")

    def test_validate_target_format_invalid(self):
        """Test target format validation with invalid inputs"""
        invalid_targets = [
            '',
            'module..function',
            '.start_with_dot',
            'end_with_dot.',
            'has-hyphen',
            'has spaces',
            '123start_with_number'
        ]
        
        for target in invalid_targets:
            with self.assertRaises(ValueError):
                Patch(target, lambda x: x)

    def test_set_replacement_force(self):
        """Test forced replacement"""
        patch_instance = Patch('test_module.test_function', lambda x: x, 'replace')
        new_replacement = lambda x: x * 4
        
        # Should work with force
        patch_instance.set_replacement(new_replacement, force=True)
        self.assertEqual(patch_instance.candidate, new_replacement)

    def test_parse_path_existing_module_function(self):
        """Test parsing existing module and function"""
        module, func = Patch.parse_path('test_module', 'test_function', False)
        self.assertEqual(module, self.test_module)
        self.assertEqual(func, self.test_module.test_function)

    def test_parse_path_existing_module_only(self):
        """Test parsing existing module without function"""
        module, func = Patch.parse_path('test_module', None, False)
        self.assertEqual(module, self.test_module)
        self.assertIsNone(func)

    @patch('importlib.import_module')
    def test_parse_path_no_create_module_not_found(self, mock_import):
        """Test module not found when create=False"""
        mock_import.side_effect = ModuleNotFoundError("Test module not found")
        
        with self.assertRaises(ModuleNotFoundError):
            Patch.parse_path('nonexistent_module', 'test_func', False)

    def test_parse_path_function_not_found_with_create(self):
        """Test function not found but create placeholder"""
        # Remove function from test module
        delattr(self.test_module, 'test_function')
        
        module, func = Patch.parse_path('test_module', 'test_function', True)
        self.assertTrue(hasattr(module, 'test_function'))
        # Should be a placeholder function
        with self.assertRaises(NotImplementedError):
            func(5)

    def test_apply_patch_replace(self):
        """Test applying replacement patch"""
        original_func = self.test_module.test_function
        replacement = lambda x: x * 3
        
        patch_instance = Patch('test_module.test_function', replacement, 'replace')
        patch_instance.apply_patch()
        
        self.assertEqual(self.test_module.test_function(2), 6)
        self.assertTrue(patch_instance.applied)


class TestPatcher(unittest.TestCase):
    """Test Patcher class functionality"""

    def setUp(self):
        # Clear patches before each test
        Patcher.patches.clear()
        
        # Create test module
        self.test_module = types.ModuleType('test_module')
        self.test_module.test_function = lambda x: x * 2
        sys.modules['test_module'] = self.test_module

    def tearDown(self):
        Patcher.patches.clear()
        for mod in list(sys.modules.keys()):
            if mod.startswith('test_'):
                del sys.modules[mod]

    def test_register_patch_new(self):
        """Test registering a new patch"""
        replacement = lambda x: x * 3
        Patcher.register_patch('test_module.test_function', replacement, 'replace')
        
        self.assertIn('test_module.test_function', Patcher.patches)
        patch_instance = Patcher.patches['test_module.test_function']
        self.assertEqual(patch_instance.candidate, replacement)

    def test_register_patch_existing_replace(self):
        """Test replacing existing patch"""
        replacement1 = lambda x: x * 3
        replacement2 = lambda x: x * 4
        
        Patcher.register_patch('test_module.test_function', replacement1, 'replace')
        Patcher.register_patch('test_module.test_function', replacement2, 'replace', force=True)
        
        patch_instance = Patcher.patches['test_module.test_function']
        self.assertEqual(patch_instance.candidate, replacement2)

    def test_register_patch_existing_decorate(self):
        """Test adding decorator to existing patch"""
        replacement = lambda x: x * 3
        decorator = lambda func: lambda x: func(x) + 1
        
        Patcher.register_patch('test_module.test_function', replacement, 'replace')
        Patcher.register_patch('test_module.test_function', decorator, 'decorate')
        
        patch_instance = Patcher.patches['test_module.test_function']
        self.assertEqual(len(patch_instance.wrappers), 1)
        self.assertEqual(patch_instance.wrappers[0], decorator)

    def test_apply_patches(self):
        """Test applying all registered patches"""
        replacement = lambda x: x * 3
        Patcher.register_patch('test_module.test_function', replacement, 'replace')
        
        # Function should still be original before applying
        self.assertEqual(self.test_module.test_function(2), 4)
        
        Patcher.apply_patches()
        
        # Function should be replaced after applying
        self.assertEqual(self.test_module.test_function(2), 6)

    def test_apply_patches_with_error(self):
        """Test applying patches when one fails"""
        # Create a patch that will fail
        Patcher.register_patch('nonexistent_module.function', lambda x: x, 'replace', create=False)
        
        # Should not raise exception but continue
        try:
            Patcher.apply_patches()
        except Exception as e:
            self.fail(f"apply_patches should handle exceptions gracefully: {e}")


class TestSecurity(unittest.TestCase):
    """Test security-related functionality"""

    def test_security_error_creation(self):
        """Test SecurityError exception"""
        error = SecurityError("Test security error")
        self.assertEqual(str(error), "Test security error")

    @patch('importlib.import_module')
    def test_parse_path_security_restricted_module(self, mock_import):
        """Test security restrictions on module creation"""
        mock_import.side_effect = ModuleNotFoundError("Module not found")
        
        with self.assertRaises(SecurityError):
            Patch.parse_path('sys.malicious', 'function', True)


if __name__ == '__main__':
    unittest.main()