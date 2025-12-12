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
from unittest.mock import Mock, patch, MagicMock
import argparse
from typing import Optional

from mindie_turbo.utils.cli import parser, parse_custom_args
from mindie_turbo.utils.patcher import Patcher
from mindie_turbo.adaptor.base_turbo import BaseTurbo, TurboPatch


class TestBaseTurbo(unittest.TestCase):
    """Test cases for BaseTurbo abstract base class."""

    def setUp(self):
        class ConcreteTurbo(BaseTurbo):
            def __init__(self):
                super().__init__()
                self.check_env_called = False
                self.setup_env_called = False
                self.register_patches_called = False
                self.register_env_patches_called = False

            @property
            def args(self) -> argparse.Namespace:
                return argparse.Namespace()

            def check_environment(self) -> None:
                self.check_env_called = True

            def setup_environment(self) -> None:
                self.setup_env_called = True

            def register_patches(self, level: int) -> None:
                self.register_patches_called = True
                self.registered_level = level

            def register_env_patches(self) -> None:
                self.register_env_patches_called = True

            def activate_extra_patches(self, patch_type: str) -> None:
                pass

        self.concrete_turbo = ConcreteTurbo()

    def test_initialization(self):
        """Test BaseTurbo initialization."""
        self.assertIsNone(self.concrete_turbo._args)
        self.assertEqual(self.concrete_turbo.patcher, Patcher)
        self.assertIsInstance(self.concrete_turbo.optimization_levels, dict)
        self.assertIsInstance(self.concrete_turbo.extra_patch_mapping, dict)

    def test_optimization_levels_content(self):
        """Test optimization levels dictionary content."""
        expected_levels = {0: "basic", 1: "advanced", 2: "high-advanced", 3: "experimental"}
        self.assertEqual(self.concrete_turbo.optimization_levels, expected_levels)

    def test_activate_with_valid_level(self):
        """Test activate method with valid level."""
        with patch.object(self.concrete_turbo.patcher, 'apply_patches') as mock_apply:
            self.concrete_turbo.activate(1)
            
            self.assertTrue(self.concrete_turbo.check_env_called)
            self.assertTrue(self.concrete_turbo.setup_env_called)
            self.assertTrue(self.concrete_turbo.register_patches_called)
            self.assertEqual(self.concrete_turbo.registered_level, 1)
            self.assertTrue(self.concrete_turbo.register_env_patches_called)
            mock_apply.assert_called_once()

    def test_activate_with_string_level(self):
        """Test activate method with string level that can be converted to int."""
        with patch.object(self.concrete_turbo.patcher, 'apply_patches'):
            self.concrete_turbo.activate("2")
            self.assertEqual(self.concrete_turbo.registered_level, 2)

    def test_activate_with_min_level(self):
        """Test activate method with minimum level."""
        with patch.object(self.concrete_turbo.patcher, 'apply_patches'):
            self.concrete_turbo.activate(0)
            self.assertEqual(self.concrete_turbo.registered_level, 0)

    def test_activate_with_max_level(self):
        """Test activate method with maximum level."""
        with patch.object(self.concrete_turbo.patcher, 'apply_patches'):
            self.concrete_turbo.activate(3)
            self.assertEqual(self.concrete_turbo.registered_level, 3)

    def test_activate_with_invalid_type(self):
        """Test activate method with invalid type that cannot be converted to int."""
        with self.assertRaises(TypeError):
            self.concrete_turbo.activate([1, 2, 3])

    def test_activate_with_invalid_string(self):
        """Test activate method with string that cannot be converted to int."""
        with self.assertRaises(TypeError):
            self.concrete_turbo.activate("invalid")

    def test_activate_with_level_too_low(self):
        """Test activate method with level below minimum."""
        with self.assertRaises(ValueError):
            self.concrete_turbo.activate(-1)

    def test_activate_with_level_too_high(self):
        """Test activate method with level above maximum."""
        with self.assertRaises(ValueError):
            self.concrete_turbo.activate(4)


class TestTurboPatch(unittest.TestCase):
    """Test cases for TurboPatch singleton class."""

    def setUp(self):
        # Reset the singleton before each test
        TurboPatch._frontend = None
        TurboPatch.is_faquant = False

    def test_initial_state(self):
        """Test initial state of TurboPatch."""
        self.assertIsNone(TurboPatch._frontend)
        self.assertFalse(TurboPatch.is_faquant)

    def test_set_frontend_first_time(self):
        """Test setting frontend for the first time."""
        mock_frontend = Mock()
        TurboPatch.set_frontend(mock_frontend)
        self.assertEqual(TurboPatch._frontend, mock_frontend)

    def test_set_frontend_multiple_times(self):
        """Test that frontend can only be set once."""
        mock_frontend1 = Mock()
        mock_frontend2 = Mock()
        
        TurboPatch.set_frontend(mock_frontend1)
        TurboPatch.set_frontend(mock_frontend2)  # This should not change the frontend
        
        self.assertEqual(TurboPatch._frontend, mock_frontend1)

    def test_activate_extra_patches_with_frontend(self):
        """Test activate_extra_patches when frontend is set."""
        mock_frontend = Mock()
        TurboPatch.set_frontend(mock_frontend)
        
        TurboPatch.activate_extra_patches("test_patch")
        mock_frontend.activate_extra_patches.assert_called_once_with("test_patch")

    def test_is_faquant_property(self):
        """Test is_faquant property can be modified."""
        TurboPatch.is_faquant = True
        self.assertTrue(TurboPatch.is_faquant)
        
        TurboPatch.is_faquant = False
        self.assertFalse(TurboPatch.is_faquant)


if __name__ == '__main__':
    unittest.main()