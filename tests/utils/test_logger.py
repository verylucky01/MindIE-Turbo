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
import logging
import logging.handlers
import os
import tempfile
import shutil
import stat
from io import StringIO

# Import the correct function names
from mindie_turbo.utils.logger import (
    setup_logger,
    _validate_log_configuration,  # Fixed function name
    _validate_directory,          # Fixed function name
    _check_disk_space,           # Fixed function name
    DiskSpaceError,              # Added DiskSpaceError
    logger
)


class TestSetupLogger(unittest.TestCase):
    """Test cases for setup_logger function."""

    def setUp(self):
        self.original_handlers = {}
        self.original_levels = {}
        
        self.test_dir = tempfile.mkdtemp()
        
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        for name, handlers in self.original_handlers.items():
            log = logging.getLogger(name)
            log.handlers = handlers
            log.setLevel(self.original_levels.get(name, logging.NOTSET))

    def test_setup_logger_basic(self):
        """Test basic logger setup without file output."""
        logger_name = "test_basic_logger"
        test_logger = setup_logger(name=logger_name, log_file=None)
        
        self.assertEqual(test_logger.name, logger_name)
        self.assertEqual(test_logger.level, logging.INFO)
        # Should have only 1 StreamHandler
        stream_handlers = [h for h in test_logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertEqual(len(stream_handlers), 1)
        self.assertFalse(test_logger.propagate)

    @patch('mindie_turbo.utils.logger._validate_log_configuration')
    def test_setup_logger_with_file(self, mock_validate):
        """Test logger setup with file output."""
        logger_name = "test_file_logger"
        log_file = os.path.join(self.test_dir, "test.log")
        
        test_logger = setup_logger(name=logger_name, log_file=log_file)
        
        self.assertEqual(test_logger.name, logger_name)
        mock_validate.assert_called_once_with(log_file, 10 * 1024 * 1024)

    def test_setup_logger_custom_level(self):
        """Test logger setup with custom log level."""
        logger_name = "test_custom_level"
        
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            with self.subTest(level=level):
                test_logger = setup_logger(name=logger_name, level=level)
                self.assertEqual(test_logger.level, level)

    def test_setup_logger_custom_format(self):
        """Test logger setup with custom format."""
        logger_name = "test_custom_format"
        custom_fmt = "%(levelname)s - %(message)s"
        
        test_logger = setup_logger(name=logger_name, fmt=custom_fmt)
        
        handler = test_logger.handlers[0]
        self.assertEqual(handler.formatter._fmt, custom_fmt)

    def test_setup_logger_clears_existing_handlers(self):
        """Test that setup_logger clears existing handlers."""
        logger_name = "test_clear_handlers"
        
        test_logger = logging.getLogger(logger_name)
        test_logger.addHandler(logging.StreamHandler())
        test_logger.addHandler(logging.StreamHandler())

        test_logger = setup_logger(name=logger_name)
        
        self.assertEqual(len(test_logger.handlers), 1)

    @patch('mindie_turbo.utils.logger._validate_log_configuration')
    def test_setup_logger_file_validation_called(self, mock_validate):
        """Test that file validation is called when log_file is provided."""
        logger_name = "test_validation"
        log_file = os.path.join(self.test_dir, "validation_test.log")
        
        setup_logger(name=logger_name, log_file=log_file)
        
        mock_validate.assert_called_once_with(log_file, 10 * 1024 * 1024)


class TestValidateDirectory(unittest.TestCase):
    """Test cases for _validate_directory function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_validate_directory_existing(self):
        """Test validation for existing directory."""
        _validate_directory(self.test_dir)

    def test_validate_directory_new(self):
        """Test validation for new directory."""
        new_dir = os.path.join(self.test_dir, "new_subdir")
        _validate_directory(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    @patch('os.makedirs')
    def test_validate_directory_creation_failure(self, mock_makedirs):
        """Test validation when directory creation fails."""
        mock_makedirs.side_effect = OSError("Creation failed")
        new_dir = os.path.join(self.test_dir, "non_existent")
        
        with self.assertRaises(OSError):
            _validate_directory(new_dir)


class TestCheckDiskSpace(unittest.TestCase):
    """Test cases for _check_disk_space function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('shutil.disk_usage')
    def test_check_disk_space_sufficient(self, mock_disk_usage):
        """Test disk space check with sufficient space."""
        mock_disk_usage.return_value = MagicMock(free=20 * 1024 * 1024)  # 20MB
        _check_disk_space(self.test_dir, 10 * 1024 * 1024)  # Need 10MB

    @patch('shutil.disk_usage')
    def test_check_disk_space_insufficient(self, mock_disk_usage):
        """Test disk space check with insufficient space."""
        mock_disk_usage.return_value = MagicMock(free=5 * 1024 * 1024)  # 5MB
        
        with self.assertRaises(DiskSpaceError):
            _check_disk_space(self.test_dir, 10 * 1024 * 1024)  # Need 10MB


class TestModuleLevelLogger(unittest.TestCase):
    """Test cases for module-level logger initialization."""

    def test_module_logger_initialization(self):
        """Test that the module-level logger is properly initialized."""
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "MindIE-Turbo")
        self.assertEqual(logger.level, logging.ERROR)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_setup_logger_with_special_characters_in_name(self):
        """Test logger setup with special characters in name."""
        test_logger = setup_logger(name="test.logger@domain.com")
        self.assertEqual(test_logger.name, "test.logger@domain.com")

    @patch('mindie_turbo.utils.logger._validate_log_configuration')
    def test_setup_logger_empty_file_path(self, mock_validate):
        """Test setup_logger with empty file path."""
        test_logger = setup_logger(name="test_empty", log_file="")
        # Should not call validation as file path is empty
        mock_validate.assert_not_called()

    @patch('logging.handlers.RotatingFileHandler')
    @patch('logging.FileHandler')
    def test_setup_logger_rotating_handler_fallback(self, mock_file_handler, mock_rotating_handler):
        """Test that setup_logger falls back to FileHandler when RotatingFileHandler fails."""
        mock_rotating_handler.side_effect = Exception("Rotation failed")
        
        log_file = os.path.join(self.test_dir, "test.log")
        test_logger = setup_logger(name="test_fallback", log_file=log_file)
        
        # Should create FileHandler as fallback
        mock_file_handler.assert_called_once()


if __name__ == '__main__':
    unittest.main()