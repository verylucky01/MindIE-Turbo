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
import tempfile
import os
import stat
from unittest.mock import patch, mock_open
from functools import reduce

import pytest

from mindie_turbo.utils.file_utils import (
    safe_open,
    standardize_path,
    is_path_exists,
    check_path_is_none,
    check_path_is_link,
    check_path_is_str,
    check_path_has_special_characters,
    check_path_length_lt,
    check_file_size_lt,
    check_owner,
    check_other_write_permission,
    check_path_permission,
    check_file_safety,
    safe_listdir,
    safe_chmod,
    has_owner_write_permission,
    safe_readlines,
    MAX_PATH_LENGTH,
    MAX_FILE_SIZE,
    MAX_FILENUM_PER_DIR,
    MAX_LINENUM_PER_FILE
)


class TestSafeFileOperations(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory and file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False)
        self.test_file.write(b"test content")
        self.test_file.close()
        
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_standardize_path(self):
        # Test normal path
        result = standardize_path(self.test_file.name)
        self.assertEqual(result, os.path.realpath(self.test_file.name))
        
        # Test path is None
        with self.assertRaises(TypeError):
            standardize_path(None)
            
        # Test path length exceeds limit
        long_path = "a" * (MAX_PATH_LENGTH + 1)
        with self.assertRaises(ValueError):
            standardize_path(long_path)
    
    @patch('os.path.islink')
    def test_check_path_is_link(self, mock_islink):
        mock_islink.return_value = True
        with self.assertRaises(ValueError):
            check_path_is_link("/fake/path")
    
    def test_check_path_is_none(self):
        with self.assertRaises(TypeError):
            check_path_is_none(None)
    
    def test_check_path_is_str(self):
        with self.assertRaises(TypeError):
            check_path_is_str(123)
    
    def test_check_path_has_special_characters(self):
        # Test path with special characters
        with self.assertRaises(ValueError):
            check_path_has_special_characters("/path/with*star")
        with self.assertRaises(ValueError):
            check_path_has_special_characters("/path/with?question")
    
    def test_check_path_length_lt(self):
        # Test normal length
        check_path_length_lt("a" * MAX_PATH_LENGTH)
        
        # Test path length exceeds limit
        with self.assertRaises(ValueError):
            check_path_length_lt("a" * (MAX_PATH_LENGTH + 1))
    
    def test_check_file_size_lt(self):
        # Create a small file
        small_file = tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False)
        small_file.write(b"small")
        small_file.close()
        
        # Test normal file size
        check_file_size_lt(small_file.name, MAX_FILE_SIZE)
        
        # Test oversized file (simulated)
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = MAX_FILE_SIZE + 1
            with self.assertRaises(ValueError):
                check_file_size_lt(small_file.name, MAX_FILE_SIZE)
        
        os.unlink(small_file.name)
    
    @patch('os.geteuid')
    @patch('os.getgid')
    def test_check_owner(self, mock_getgid, mock_geteuid):
        mock_geteuid.return_value = 1000
        mock_getgid.return_value = 1000
        
        # Mock file owner and group
        with patch('os.stat') as mock_stat:
            mock_stat.return_value.st_uid = 1001  # Different user
            mock_stat.return_value.st_gid = 1001  # Different group
            
            with self.assertRaises(PermissionError):
                check_owner(self.test_file.name)
    
    def test_check_other_write_permission(self):
        # Create file without other write permission
        no_other_write_file = tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False)
        no_other_write_file.close()
        os.chmod(no_other_write_file.name, 0o644)  # No other write permission
        
        # Should not raise exception
        check_other_write_permission(no_other_write_file.name)
        
        # Create file with other write permission
        other_write_file = tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False)
        other_write_file.close()
        os.chmod(other_write_file.name, 0o666)  # Has other write permission
        
        with self.assertRaises(PermissionError):
            check_other_write_permission(other_write_file.name)
        
        os.unlink(no_other_write_file.name)
        os.unlink(other_write_file.name)
    
    def test_check_file_safety(self):
        # Test existing file
        check_file_safety(self.test_file.name, 'r', True)
        
        # Test non-existent file (read mode)
        with self.assertRaises(FileNotFoundError):
            check_file_safety("/nonexistent/file", 'r', True)
        
        # Test non-existent file (write mode)
        # Should not raise exception
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        check_file_safety(nonexistent_file, 'w', True)
    
    def test_safe_listdir(self):
        # Create test files
        test_files = []
        for _ in range(5):
            test_file = tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False)
            test_files.append(test_file.name)
            test_file.close()
        
        # Test normal case
        files = safe_listdir(self.temp_dir)
        self.assertGreaterEqual(len(files), 5)
        
        # Test file count exceeds limit
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = list(range(MAX_FILENUM_PER_DIR + 1))
            with self.assertRaises(ValueError):
                safe_listdir(self.temp_dir)
        
        # Clean up
        for file in test_files:
            os.unlink(file)
    
    def test_safe_chmod(self):
        # Test normal permission change
        safe_chmod(self.test_file.name, 0o644)
        self.assertEqual(stat.S_IMODE(os.stat(self.test_file.name).st_mode), 0o644)
    
    def test_has_owner_write_permission(self):
        # Test with write permission
        os.chmod(self.test_file.name, 0o644)  # Has user write permission
        self.assertTrue(has_owner_write_permission(self.test_file.name))
        
        # Test without write permission
        os.chmod(self.test_file.name, 0o444)  # No user write permission
        self.assertFalse(has_owner_write_permission(self.test_file.name))
    
    def test_safe_readlines(self):
        # Create test file
        test_content = "line1\nline2\nline3\n"
        with open(self.test_file.name, 'w') as f:
            f.write(test_content)
        
        # Test normal read
        with open(self.test_file.name, 'r') as f:
            lines = safe_readlines(f)
            self.assertEqual(len(lines), 3)
    
    def test_safe_open(self):
        # Test normal file opening
        with safe_open(self.test_file.name, 'r') as f:
            content = f.read()
            self.assertEqual(content, "test content")
        
        # Test writing to new file
        new_file = os.path.join(self.temp_dir, "new_file.txt")
        with safe_open(new_file, 'w') as f:
            f.write("new content")
        
        self.assertTrue(os.path.exists(new_file))
        with open(new_file, 'r') as f:
            self.assertEqual(f.read(), "new content")
        
        os.unlink(new_file)
    
    def test_is_path_exists(self):
        self.assertTrue(is_path_exists(self.test_file.name))
        self.assertFalse(is_path_exists("/nonexistent/path"))


if __name__ == '__main__':
    unittest.main()