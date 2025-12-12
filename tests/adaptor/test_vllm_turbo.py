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
import os
import sys
from io import StringIO

from mindie_turbo.adaptor.vllm_turbo import (
    VLLMTurbo, 
    TurboPatch, 
    get_validated_optimization_level, 
    initialize_vllm_turbo,
    DECORATE,
    logger
)


class TestVLLMTurbo(unittest.TestCase):
    """Test cases for VLLMTurbo class."""

    def setUp(self):

        self.original_env = os.environ.copy()

        TurboPatch._frontend = None
        TurboPatch.is_faquant = False

    def tearDown(self):

        os.environ.clear()
        os.environ.update(self.original_env)

    def test_decorate_constant(self):
        """Test DECORATE constant."""
        self.assertEqual(DECORATE, "decorate")

    def test_setup_environment(self):
        """Test setup_environment method."""
        turbo = VLLMTurbo()

        turbo.setup_environment()
        self.assertTrue(True)

    def test_register_patches(self):
        """Test register_patches method with different levels."""
        turbo = VLLMTurbo()
        
        for level in range(4):
            with self.subTest(level=level):
                turbo.register_patches(level)
                self.assertTrue(True)

    def test_register_extra_patches(self):
        """Test register_extra_patches method."""
        turbo = VLLMTurbo()
        turbo.register_extra_patches()

        self.assertTrue(True)

    def test_register_env_patches(self):
        """Test register_env_patches method."""
        turbo = VLLMTurbo()
        turbo.register_env_patches()

        self.assertTrue(True)

    def test_activate_extra_patches_valid(self):
        """Test activate_extra_patches with valid patch type."""
        turbo = VLLMTurbo()
        turbo.extra_patch_mapping = {"test_patch": ["target1", "target2"]}
        turbo.patcher = Mock()
        turbo.patcher.patches = {
            "target1": Mock(),
            "target2": Mock()
        }
        
        turbo.activate_extra_patches("test_patch")

        turbo.patcher.patches["target1"].apply_patch.assert_called_once()
        turbo.patcher.patches["target2"].apply_patch.assert_called_once()

    def test_activate_extra_patches_invalid(self):
        """Test activate_extra_patches with invalid patch type."""
        turbo = VLLMTurbo()
        turbo.extra_patch_mapping = {"valid_patch": []}
        
        with self.assertRaises(ValueError) as context:
            turbo.activate_extra_patches("invalid_patch")
        
        self.assertIn("Unsupported patch_type", str(context.exception))
        self.assertIn("valid_patch", str(context.exception))


class TestGetValidatedOptimizationLevel(unittest.TestCase):
    """Test cases for get_validated_optimization_level function."""

    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_value(self):
        """Test default value when environment variable is not set."""
        if 'VLLM_OPTIMIZATION_LEVEL' in os.environ:
            del os.environ['VLLM_OPTIMIZATION_LEVEL']
        
        level = get_validated_optimization_level()
        self.assertEqual(level, 2)

    def test_valid_values(self):
        """Test valid environment variable values."""
        for valid_value in ['0', '1', '2', '3']:
            with self.subTest(value=valid_value):
                os.environ['VLLM_OPTIMIZATION_LEVEL'] = valid_value
                level = get_validated_optimization_level()
                self.assertEqual(level, int(valid_value))

    def test_out_of_range_low(self):
        """Test values below valid range."""
        os.environ['VLLM_OPTIMIZATION_LEVEL'] = '-1'
        with self.assertRaises(ValueError) as context:
            get_validated_optimization_level()
        self.assertIn("out of range", str(context.exception))

    def test_out_of_range_high(self):
        """Test values above valid range."""
        os.environ['VLLM_OPTIMIZATION_LEVEL'] = '4'
        with self.assertRaises(ValueError) as context:
            get_validated_optimization_level()
        self.assertIn("out of range", str(context.exception))


class TestInitializeVLLMTurbo(unittest.TestCase):
    """Test cases for initialize_vllm_turbo function."""

    def setUp(self):
        self.original_env = os.environ.copy()

        TurboPatch._frontend = None

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        TurboPatch._frontend = None

    @patch('mindie_turbo.adaptor.vllm_turbo.VLLMTurbo')
    @patch('mindie_turbo.adaptor.vllm_turbo.logger')
    def test_successful_initialization(self, mock_logger, mock_vllm_turbo):
        """Test successful initialization with valid level."""
        os.environ['VLLM_OPTIMIZATION_LEVEL'] = '2'
        
        mock_instance = Mock()
        mock_vllm_turbo.return_value = mock_instance
        
        result = initialize_vllm_turbo()
        
        self.assertEqual(result, mock_instance)
        mock_vllm_turbo.assert_called_once()
        mock_instance.activate.assert_called_once_with(2)
        mock_instance.register_extra_patches.assert_called_once()
        mock_logger.info.assert_called_with("vLLM Turbo activated with optimization level: 2")

    @patch('mindie_turbo.adaptor.vllm_turbo.VLLMTurbo')
    @patch('mindie_turbo.adaptor.vllm_turbo.logger')
    def test_fallback_also_fails(self, mock_logger, mock_vllm_turbo):
        """Test when both main and fallback initialization fail."""
        os.environ['VLLM_OPTIMIZATION_LEVEL'] = 'invalid'
        
        mock_instance = Mock()
        mock_instance.activate.side_effect = Exception("Fallback also failed")
        mock_vllm_turbo.return_value = mock_instance
        
        result = initialize_vllm_turbo()
        
        self.assertIsNone(result)
        mock_logger.error.assert_called()

    @patch('mindie_turbo.adaptor.vllm_turbo.VLLMTurbo')
    @patch('mindie_turbo.adaptor.vllm_turbo.logger')
    def test_general_exception(self, mock_logger, mock_vllm_turbo):
        """Test handling of general exceptions during initialization."""
        mock_vllm_turbo.side_effect = Exception("General failure")
        
        result = initialize_vllm_turbo()
        
        self.assertIsNone(result)
        mock_logger.error.assert_called_with("Failed to initialize vLLM Turbo: General failure")


if __name__ == '__main__':
    unittest.main()
