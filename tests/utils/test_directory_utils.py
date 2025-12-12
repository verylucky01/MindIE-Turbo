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
import tempfile
import stat
import logging
from unittest.mock import patch, MagicMock
import pytest

from mindie_turbo.utils.directory_utils import (
    check_directory_path,
    standardize_directory_path,
    check_path_is_none,
    check_path_is_str,
    check_path_is_link,
    check_directory_path_characters,
    check_path_length_lt,
    check_directory_owner,
    check_directory_permissions,
    check_directory_other_permissions,
    check_directory_safety,
    safe_listdir,
    safe_walk,
    safe_mkdir,
    safe_rmdir,
    MAX_PATH_LENGTH,
    MAX_DIR_FILES
)


class TestDirectoryUtils:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = tempfile.NamedTemporaryFile(delete=False).name
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
    
    # Test check_path_is_none
    def test_check_path_is_none_valid(self):
        """Test check_path_is_none with valid input"""
        check_path_is_none("/valid/path")
    
    def test_check_path_is_none_invalid(self):
        """Test check_path_is_none with None input"""
        with pytest.raises(TypeError):
            check_path_is_none(None)
    
    # Test check_path_is_str
    def test_check_path_is_str_valid(self):
        """Test check_path_is_str with string input"""
        check_path_is_str("/valid/path")
    
    def test_check_path_is_str_invalid(self):
        """Test check_path_is_str with non-string input"""
        with pytest.raises(TypeError):
            check_path_is_str(123)
    
    # Test check_path_is_link
    def test_check_path_is_link_valid(self, tmp_path):
        """Test check_path_is_link with non-link path"""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        check_path_is_link(str(test_file))
    
    @patch('os.path.islink')
    def test_check_path_is_link_invalid(self, mock_islink):
        """Test check_path_is_link with symbolic link"""
        mock_islink.return_value = True
        with pytest.raises(ValueError):
            check_path_is_link("/symlink/path")
    
    # Test check_directory_path_characters
    def test_check_directory_path_characters_valid(self):
        """Test check_directory_path_characters with valid characters"""
        valid_paths = [
            "/home/user/test",
            "/var/log/app",
            "/tmp/123_test",
            "/path/with-chars"
        ]
        for path in valid_paths:
            check_directory_path_characters(path)
    
    def test_check_directory_path_characters_invalid(self):
        """Test check_directory_path_characters with dangerous characters"""
        dangerous_paths = [
            "/home/user|test",
            "/var/log/app*",
            "/tmp/test?.txt",
            "/path/with[bad]chars"
        ]
        for path in dangerous_paths:
            with pytest.raises(ValueError):
                check_directory_path_characters(path)
    
    # Test check_path_length_lt
    def test_check_path_length_lt_valid(self):
        """Test check_path_length_lt with valid length"""
        short_path = "/short/path"
        check_path_length_lt(short_path)
    
    def test_check_path_length_lt_invalid(self):
        """Test check_path_length_lt with excessive length"""
        long_path = "a" * (MAX_PATH_LENGTH + 1)
        with pytest.raises(ValueError):
            check_path_length_lt(long_path)
    
    # Test check_directory_owner
    @patch('os.stat')
    @patch('os.geteuid')
    @patch('os.getgid')
    def test_check_directory_owner_valid(self, mock_getgid, mock_geteuid, mock_stat):
        """Test check_directory_owner with valid permissions"""
        mock_stat.return_value.st_uid = 1000
        mock_stat.return_value.st_gid = 1000
        mock_geteuid.return_value = 1000
        mock_getgid.return_value = 1000
        
        check_directory_owner("/test/path")
    
    @patch('os.stat')
    @patch('os.geteuid')
    @patch('os.getgid')
    def test_check_directory_owner_invalid(self, mock_getgid, mock_geteuid, mock_stat):
        """Test check_directory_owner with invalid permissions"""
        mock_stat.return_value.st_uid = 1001
        mock_stat.return_value.st_gid = 1001
        mock_geteuid.return_value = 1000
        mock_getgid.return_value = 1000
        
        with pytest.raises(PermissionError):
            check_directory_owner("/test/path")
    
    # Test check_directory_permissions
    def test_check_directory_permissions_read_valid(self):
        """Test check_directory_permissions with read access"""
        os.chmod(self.test_dir, 0o755)
        check_directory_permissions(self.test_dir, 'r')
    
    def test_check_directory_permissions_write_valid(self):
        """Test check_directory_permissions with write access"""
        os.chmod(self.test_dir, 0o755)
        check_directory_permissions(self.test_dir, 'w')
    
    def test_check_directory_permissions_nonexistent(self):
        """Test check_directory_permissions with non-existent directory"""
        with pytest.raises(FileNotFoundError):
            check_directory_permissions("/nonexistent/path", 'r')
    
    def test_check_directory_permissions_not_directory(self):
        """Test check_directory_permissions with file instead of directory"""
        with pytest.raises(ValueError):
            check_directory_permissions(self.test_file, 'r')
    
    # Test check_directory_other_permissions
    def test_check_directory_other_permissions_safe(self):
        """Test check_directory_other_permissions with safe permissions"""
        os.chmod(self.test_dir, 0o755)  # Others have read/execute but not write
        # Should not raise exception, only log warning if others have write
        check_directory_other_permissions(self.test_dir)
    
    # Test check_directory_safety
    def test_check_directory_safety_exist_ok(self):
        """Test check_directory_safety with existing directory and exist_ok=True"""
        check_directory_safety(self.test_dir, 'r', is_exist_ok=True)
    
    def test_check_directory_safety_exist_not_ok(self):
        """Test check_directory_safety with existing directory and exist_ok=False"""
        with pytest.raises(FileExistsError):
            check_directory_safety(self.test_dir, 'r', is_exist_ok=False)
    
    def test_check_directory_safety_nonexistent_read(self):
        """Test check_directory_safety with non-existent directory for read mode"""
        nonexistent_path = os.path.join(self.test_dir, "nonexistent")
        with pytest.raises(FileNotFoundError):
            check_directory_safety(nonexistent_path, 'r', is_exist_ok=True)
    
    def test_check_directory_safety_nonexistent_write(self):
        """Test check_directory_safety with non-existent directory for write mode"""
        nonexistent_path = os.path.join(self.test_dir, "nonexistent")
        # Should not raise exception for write mode with non-existent directory
        check_directory_safety(nonexistent_path, 'w', is_exist_ok=True)
    
    # Test standardize_directory_path
    def test_standardize_directory_path_valid(self):
        """Test standardize_directory_path with valid input"""
        result = standardize_directory_path(self.test_dir)
        assert os.path.isabs(result)
        assert result == os.path.realpath(self.test_dir)
    
    @patch('os.path.islink')
    def test_standardize_directory_path_with_link_check(self, mock_islink):
        """Test standardize_directory_path with link checking"""
        mock_islink.return_value = True
        with pytest.raises(ValueError):
            standardize_directory_path("/symlink/path")
    
    # Test check_directory_path
    def test_check_directory_path_read_valid(self):
        """Test check_directory_path with read mode"""
        result = check_directory_path(self.test_dir, 'r')
        assert result == os.path.realpath(self.test_dir)
    
    def test_check_directory_path_write_valid(self):
        """Test check_directory_path with write mode"""
        result = check_directory_path(self.test_dir, 'w')
        assert result == os.path.realpath(self.test_dir)
    
    # Test safe_listdir
    def test_safe_listdir_valid(self):
        """Test safe_listdir with valid directory"""
        # Create some test files
        test_files = ['test1.txt', 'test2.txt', 'test3.txt']
        for file in test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write("test")
        
        result = safe_listdir(self.test_dir)
        assert len(result) == 3
        assert all(file in result for file in test_files)
    
    # Test safe_walk
    def test_safe_walk_valid(self):
        """Test safe_walk with valid directory structure"""
        # Create test directory structure
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)
        
        with open(os.path.join(self.test_dir, "file1.txt"), 'w') as f:
            f.write("test")
        with open(os.path.join(subdir, "file2.txt"), 'w') as f:
            f.write("test")
        
        results = safe_walk(self.test_dir)
        assert len(results) == 2  # Root and subdir
    
    def test_safe_walk_max_depth(self):
        """Test safe_walk with depth limitation"""
        # Create deep directory structure
        current_dir = self.test_dir
        for i in range(5):
            current_dir = os.path.join(current_dir, f"level{i}")
            os.makedirs(current_dir)
        
        results = safe_walk(self.test_dir, max_depth=2)
        # Should only include directories up to depth 2
        assert len(results) <= 3  # Root + 2 levels
    
    # Test safe_mkdir
    def test_safe_mkdir_valid(self):
        """Test safe_mkdir with valid new directory"""
        new_dir = os.path.join(self.test_dir, "new_directory")
        result = safe_mkdir(new_dir)
        assert os.path.exists(new_dir)
        assert result == os.path.realpath(new_dir)
    
    # Test safe_rmdir
    def test_safe_rmdir_valid(self):
        """Test safe_rmdir with valid directory"""
        # Create a directory to remove
        dir_to_remove = os.path.join(self.test_dir, "to_remove")
        os.makedirs(dir_to_remove)
        
        safe_rmdir(dir_to_remove)
        assert not os.path.exists(dir_to_remove)
    
    @patch('shutil.rmtree')
    def test_safe_rmdir_failure(self, mock_rmtree):
        """Test safe_rmdir with removal failure"""
        mock_rmtree.side_effect = OSError("Removal failed")
        
        with pytest.raises(OSError):
            safe_rmdir(self.test_dir)
    
    def test_relative_path(self):
        """Test with relative path"""
        relative_path = "relative/path"
        result = check_directory_path(relative_path, 'w')
        assert os.path.isabs(result)
    
    @patch('os.access')
    def test_permission_denied(self, mock_access):
        """Test with permission denied scenario"""
        mock_access.return_value = False
        with pytest.raises(PermissionError):
            check_directory_permissions(self.test_dir, 'r')
    
    def test_special_characters_in_path(self):
        """Test with special characters in path"""
        special_dir = os.path.join(self.test_dir, "test-dir_with.special_chars")
        os.makedirs(special_dir)
        
        result = check_directory_path(special_dir, 'r')
        assert os.path.exists(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])