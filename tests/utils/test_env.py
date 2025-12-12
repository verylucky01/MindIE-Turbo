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

import os
import unittest
from unittest.mock import patch, MagicMock
from mindie_turbo.env import EnvironmentValidator, __getattr__, __dir__


class TestEnvironmentValidator(unittest.TestCase):
    """Test EnvironmentValidator class"""

    def test_validate_boolean(self):
        """Test validate_boolean"""
        # True values
        for true_val in ["1", "true", "yes"]:
            self.assertTrue(EnvironmentValidator.validate_boolean(true_val, "TEST_VAR"))

        # False values
        for false_val in ["0", "false", "no"]:
            self.assertFalse(
                EnvironmentValidator.validate_boolean(false_val, "TEST_VAR")
            )

        # None value
        self.assertFalse(EnvironmentValidator.validate_boolean(None, "TEST_VAR"))

        # Invalid values
        with self.assertRaises(ValueError):
            EnvironmentValidator.validate_boolean("invalid", "TEST_VAR")

    def test_validate_integer_valid(self):
        """Test validate_integer with valid values"""
        self.assertEqual(EnvironmentValidator.validate_integer("5", "TEST_VAR"), 5)
        self.assertEqual(
            EnvironmentValidator.validate_integer("10", "TEST_VAR", min_val=5), 10
        )
        self.assertEqual(
            EnvironmentValidator.validate_integer("15", "TEST_VAR", max_val=20), 15
        )
        self.assertIsNone(EnvironmentValidator.validate_integer(None, "TEST_VAR"))

    def test_validate_integer_invalid(self):
        """Test validate_integer with invalid values"""
        with self.assertRaises(ValueError):
            EnvironmentValidator.validate_integer("abc", "TEST_VAR")
        with self.assertRaises(ValueError):
            EnvironmentValidator.validate_integer("-1", "TEST_VAR")
        with self.assertRaises(ValueError):
            EnvironmentValidator.validate_integer("4", "TEST_VAR", min_val=5)
        with self.assertRaises(ValueError):
            EnvironmentValidator.validate_integer("25", "TEST_VAR", max_val=20)

    @patch("mindie_turbo.env.check_file_path")
    def test_validate_path(self, mock_check_file_path):
        """Test validate_path"""
        mock_check_file_path.return_value = "/valid/path"

        result = EnvironmentValidator.validate_path("/some/path", "TEST_PATH")
        self.assertEqual(result, "/valid/path")
        mock_check_file_path.assert_called_once_with("/some/path")

        self.assertIsNone(EnvironmentValidator.validate_path("", "TEST_PATH"))
        self.assertIsNone(EnvironmentValidator.validate_path(None, "TEST_PATH"))

    def test_private_validation_methods(self):
        """Test private validation methods"""
        # _validate_string_length
        with self.assertRaises(ValueError):
            EnvironmentValidator._validate_string_length("A" * 11, 10, "TEST_VAR")

        # _validate_not_none
        self.assertEqual(
            EnvironmentValidator._validate_not_none("test", "TEST_VAR"), "test"
        )
        with self.assertRaises(ValueError):
            EnvironmentValidator._validate_not_none(None, "TEST_VAR")

        # _validate_digits_only
        with self.assertRaises(ValueError):
            EnvironmentValidator._validate_digits_only("123a", "TEST_VAR")

        # _validate_enum_value
        valid_set = {"a", "b", "c"}
        EnvironmentValidator._validate_enum_value("a", valid_set, "TEST_VAR")
        with self.assertRaises(ValueError):
            EnvironmentValidator._validate_enum_value("d", valid_set, "TEST_VAR")

        # _validate_boolean_string
        for valid_bool in ["0", "1", "true", "false", "yes", "no"]:
            EnvironmentValidator._validate_boolean_string(valid_bool, "TEST_VAR")
        with self.assertRaises(ValueError):
            EnvironmentValidator._validate_boolean_string("invalid", "TEST_VAR")


if __name__ == "__main__":
    unittest.main()