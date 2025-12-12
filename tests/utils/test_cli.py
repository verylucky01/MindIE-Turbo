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
import argparse
import warnings
from io import StringIO
import sys

from mindie_turbo.utils.cli import (
    BaseConfig,
    parse_custom_args,
    _extract_and_validate_key,
    _convert_values_to_appropriate_type,
    _convert_single_value,
    _convert_multiple_values,
    _safe_set_attribute,
    _is_float,
    create_parser,
    parser
)


class TestBaseConfig(unittest.TestCase):
    """Test cases for BaseConfig class."""

    def test_base_config_initialization(self):
        """Test BaseConfig can be instantiated."""
        config = BaseConfig()
        self.assertIsInstance(config, BaseConfig)

    def test_base_config_validate(self):
        """Test BaseConfig validate method."""
        config = BaseConfig()
        # validate should not raise any exception
        config.validate()
        self.assertTrue(True)


class TestParseCustomArgs(unittest.TestCase):
    """Test cases for parse_custom_args function."""

    def setUp(self):
        # Capture warnings
        self.warning_capture = StringIO()
        self.original_showwarning = warnings.showwarning
        warnings.showwarning = self._custom_showwarning
        self.warnings = []

    def tearDown(self):
        warnings.showwarning = self.original_showwarning

    def _custom_showwarning(self, *args, **kwargs):
        """Simplified warning handler that only captures the message."""
        message = args[0] if args else kwargs.get('message', '')
        self.warnings.append(str(message))

    def test_parse_custom_args_no_unknown_args(self):
        """Test parse_custom_args with no unknown arguments."""
        args = argparse.Namespace()
        unknown = []
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result, args)
        self.assertEqual(len(self.warnings), 0)

    def test_parse_custom_args_with_unknown_args_warning(self):
        """Test parse_custom_args shows warning for unknown arguments."""
        args = argparse.Namespace()
        unknown = ['--test-arg', 'value']
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result, args)
        self.assertEqual(len(self.warnings), 1)
        self.assertIn("Detected unknown arguments", self.warnings[0])

    def test_parse_custom_args_single_valid_argument(self):
        """Test parse_custom_args with single valid argument."""
        args = argparse.Namespace()
        unknown = ['--test-arg', '42']
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result.test_arg, 42)
        self.assertEqual(len(self.warnings), 1)  # Only the unknown args warning

    def test_parse_custom_args_multiple_arguments(self):
        """Test parse_custom_args with multiple arguments."""
        args = argparse.Namespace()
        unknown = ['--arg1', 'value1', '--arg2', '123', '--arg3', 'true']
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result.arg1, 'value1')
        self.assertEqual(result.arg2, 123)
        self.assertTrue(result.arg3)
        
    def test_parse_custom_args_flag_argument(self):
        """Test parse_custom_args with flag argument (no value)."""
        args = argparse.Namespace()
        unknown = ['--flag']
        
        result = parse_custom_args(args, unknown)
        self.assertTrue(result.flag)

    def test_parse_custom_args_malformed_argument(self):
        """Test parse_custom_args with malformed argument."""
        args = argparse.Namespace()
        unknown = ['malformed', '--valid', 'value']
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result.valid, 'value')
        self.assertEqual(len(self.warnings), 2)  # Unknown args + malformed warning

    def test_parse_custom_args_overwrite_existing(self):
        """Test parse_custom_args overwriting existing attribute."""
        args = argparse.Namespace(existing_arg='old_value')
        unknown = ['--existing-arg', 'new_value']
        
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result.existing_arg, 'new_value')
        self.assertEqual(len(self.warnings), 2)  # Unknown args + overwrite warning


class TestExtractAndValidateKey(unittest.TestCase):
    """Test cases for _extract_and_validate_key function."""

    def setUp(self):
        self.warnings = []
        self.original_showwarning = warnings.showwarning
        warnings.showwarning = self._custom_showwarning

    def tearDown(self):
        warnings.showwarning = self.original_showwarning

    def _custom_showwarning(self, *args, **kwargs):
        """Simplified warning handler that only captures the message."""
        message = args[0] if args else kwargs.get('message', '')
        self.warnings.append(str(message))

    def test_extract_valid_key(self):
        """Test _extract_and_validate_key with valid key."""
        result = _extract_and_validate_key('--test-arg')
        self.assertEqual(result, 'test_arg')
        self.assertEqual(len(self.warnings), 0)

    def test_extract_invalid_key(self):
        """Test _extract_and_validate_key with invalid key."""
        result = _extract_and_validate_key('--123-invalid')
        self.assertIsNone(result)
        self.assertEqual(len(self.warnings), 1)
        self.assertIn("Invalid argument name", self.warnings[0])

    def test_extract_key_with_multiple_dashes(self):
        """Test _extract_and_validate_key with multiple dashes."""
        result = _extract_and_validate_key('--very-long-argument-name')
        self.assertEqual(result, 'very_long_argument_name')
        self.assertEqual(len(self.warnings), 0)


class TestConvertValuesToAppropriateType(unittest.TestCase):
    """Test cases for _convert_values_to_appropriate_type function."""

    def test_convert_no_values(self):
        """Test _convert_values_to_appropriate_type with no values."""
        result = _convert_values_to_appropriate_type([])
        self.assertTrue(result)

    def test_convert_multiple_values(self):
        """Test _convert_values_to_appropriate_type with multiple values."""
        result = _convert_values_to_appropriate_type(['1', '2.5', 'hello'])
        self.assertEqual(result, [1, 2.5, 'hello'])


class TestConvertSingleValue(unittest.TestCase):
    """Test cases for _convert_single_value function."""

    def test_convert_boolean_true(self):
        """Test _convert_single_value with boolean true."""
        result = _convert_single_value('true')
        self.assertTrue(result)

    def test_convert_boolean_false(self):
        """Test _convert_single_value with boolean false."""
        result = _convert_single_value('false')
        self.assertFalse(result)

    def test_convert_integer(self):
        """Test _convert_single_value with integer."""
        result = _convert_single_value('42')
        self.assertEqual(result, 42)

    def test_convert_float(self):
        """Test _convert_single_value with float."""
        result = _convert_single_value('3.14')
        self.assertEqual(result, 3.14)

    def test_convert_string(self):
        """Test _convert_single_value with string."""
        result = _convert_single_value('hello')
        self.assertEqual(result, 'hello')


class TestConvertMultipleValues(unittest.TestCase):
    """Test cases for _convert_multiple_values function."""

    def test_convert_multiple_mixed_values(self):
        """Test _convert_multiple_values with mixed types."""
        result = _convert_multiple_values(['1', 'true', '3.14', 'hello'])
        self.assertEqual(result, [1, True, 3.14, 'hello'])

    def test_convert_empty_list(self):
        """Test _convert_multiple_values with empty list."""
        result = _convert_multiple_values([])
        self.assertEqual(result, [])


class TestSafeSetAttribute(unittest.TestCase):
    """Test cases for _safe_set_attribute function."""

    def setUp(self):
        self.warnings = []
        self.original_showwarning = warnings.showwarning
        warnings.showwarning = self._custom_showwarning

    def tearDown(self):
        warnings.showwarning = self.original_showwarning
    
    def _custom_showwarning(self, *args, **kwargs):
        """Simplified warning handler that only captures the message."""
        message = args[0] if args else kwargs.get('message', '')
        self.warnings.append(str(message))

    def test_safe_set_new_attribute(self):
        """Test _safe_set_attribute with new attribute."""
        args = argparse.Namespace()
        _safe_set_attribute(args, 'new_attr', 'value')
        
        self.assertEqual(args.new_attr, 'value')
        self.assertEqual(len(self.warnings), 0)

    def test_safe_set_existing_attribute(self):
        """Test _safe_set_attribute with existing attribute."""
        args = argparse.Namespace(existing_attr='old_value')
        _safe_set_attribute(args, 'existing_attr', 'new_value')
        
        self.assertEqual(args.existing_attr, 'new_value')
        self.assertEqual(len(self.warnings), 1)
        self.assertIn("already exists", self.warnings[0])


class TestIsFloat(unittest.TestCase):
    """Test cases for _is_float function."""

    def test_is_float_valid(self):
        """Test _is_float with valid float strings."""
        self.assertTrue(_is_float('3.14'))
        self.assertTrue(_is_float('-2.5'))
        self.assertTrue(_is_float('0.0'))
        self.assertTrue(_is_float('123.456'))

    def test_is_float_invalid(self):
        """Test _is_float with invalid float strings."""
        self.assertFalse(_is_float('hello'))
        self.assertFalse(_is_float('123abc'))
        self.assertFalse(_is_float(''))
        self.assertFalse(_is_float('3.14.15'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete flow."""

    def setUp(self):
        self.warnings = []
        self.original_showwarning = warnings.showwarning
        warnings.showwarning = self._custom_showwarning

    def tearDown(self):
        warnings.showwarning = self.original_showwarning
    
    def _custom_showwarning(self, *args, **kwargs):
        """Simplified warning handler that only captures the message."""
        message = args[0] if args else kwargs.get('message', '')
        self.warnings.append(str(message))

    def test_complete_flow_with_parse_known_args(self):
        """Test complete integration with parse_known_args."""
        test_parser = argparse.ArgumentParser()
        test_parser.add_argument('--known-arg', type=str, default='default')
        
        # Simulate command line arguments
        test_args = ['--known-arg', 'known_value', '--unknown-arg', '42', '--flag']
        args, unknown = test_parser.parse_known_args(test_args)
        
        # Parse unknown arguments
        result = parse_custom_args(args, unknown)
        
        self.assertEqual(result.known_arg, 'known_value')
        self.assertEqual(result.unknown_arg, 42)
        self.assertEqual(len(self.warnings), 1)  # Unknown args warning


if __name__ == '__main__':
    unittest.main()