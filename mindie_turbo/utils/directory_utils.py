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
import re
import stat
import logging
from typing import List

MAX_PATH_LENGTH = 4096
MAX_DIR_FILES = 10000  # Maximum number of files limit in a directory


def check_directory_path(dir_path: str, mode='r', is_exist_ok=True, **kwargs):
    """
    Check directory path safety
    :param dir_path: Directory path
    :param mode: Access mode 'r'=read-only, 'w'=write
    :param is_exist_ok: Whether to allow the directory to already exist
    :return: Standardized directory path
    """
    max_path_length = kwargs.get('max_path_length', MAX_PATH_LENGTH)
    check_link = kwargs.get('check_link', True)

    dir_path = standardize_directory_path(dir_path, max_path_length, check_link)
    check_directory_safety(dir_path, mode, is_exist_ok)
    return dir_path


def standardize_directory_path(path: str, max_path_length=MAX_PATH_LENGTH, check_link=True):
    """
    Standardize directory path and perform basic checks
    """
    check_path_is_none(path)
    check_path_is_str(path)
    
    check_path_length_lt(path, max_path_length)
    
    if check_link:
        check_path_is_link(path)
    
    path = os.path.realpath(path)
    check_directory_path_characters(path)
    return path


def check_path_is_none(path: str):
    if path is None:
        raise TypeError("The directory path should not be None.")


def check_path_is_str(path: str):
    if not isinstance(path, str):
        raise TypeError(f"The directory path's type should be str, but get {type(path)}.")


def check_path_is_link(path: str):
    if os.path.islink(os.path.normpath(path)):
        raise ValueError("The path should not be a symbolic link. "
                         f"Please check the input path: {path}")


def check_directory_path_characters(path: str):
    """
    Check directory path character safety
    """
    # Allow letters, numbers, common symbols, Chinese characters, and other legal directory characters
    pattern = re.compile(r"[^0-9a-zA-Z_./-]")
    dangerous_chars = pattern.findall(path)
    
    if dangerous_chars:
        raise ValueError(f"Directory path contains dangerous characters: {set(dangerous_chars)}. "
                         f"Please check the input path: {path}")


def check_path_length_lt(path: str, max_path_length=MAX_PATH_LENGTH):
    path_length = len(path)
    if path_length > max_path_length:
        raise ValueError(f"The length of path should not be greater than {max_path_length}, but got {path_length}. "
                         f"Please check the input path within the valid length range: {path[:max_path_length]}.")


def check_directory_owner(dir_path: str):
    """
    Check directory owner permissions
    """
    dir_stat = os.stat(dir_path)
    dir_owner, dir_gid = dir_stat.st_uid, dir_stat.st_gid
    cur_uid = os.geteuid()
    cur_gid = os.getgid()
    
    if not (cur_uid == 0 or cur_uid == dir_owner or dir_gid == cur_gid):
        raise PermissionError(f"The current user does not have permission to access the directory: {dir_path}. "
                              "Because he is not root or the directory owner, "
                              "and not in the same user group with the directory owner.")


def check_directory_permissions(dir_path: str, mode: str):
    """
    Check directory permissions
    """
    # Check if directory exists
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")
    
    # Check if it's a directory
    if not os.path.isdir(dir_path):
        raise ValueError(f"Path exists but is not a directory: {dir_path}")
    
    # Check permissions based on access mode
    if mode in ['r', 'r+', 'w+', 'a+']:
        if not os.access(dir_path, os.R_OK | os.X_OK):
            raise PermissionError(f"No read permission for directory: {dir_path}")
    
    if mode in ['w', 'a', 'r+', 'w+', 'a+']:
        if not os.access(dir_path, os.W_OK | os.X_OK):
            raise PermissionError(f"No write permission for directory: {dir_path}")


def check_directory_other_permissions(dir_path: str):
    """
    Check directory other user permissions
    """
    dir_stat = os.stat(dir_path)
    mode = dir_stat.st_mode
    
    # Check if other users have write permission (warning level, can be adjusted as needed)
    if mode & stat.S_IWOTH:
        logging.warning(f"Directory is writable by others: {dir_path}")
        raise PermissionError(f"Directory should not be writable by others: {dir_path}")


def check_directory_safety(dir_path: str, mode='r', is_exist_ok=True):
    """
    Main directory safety check function
    """
    if os.path.exists(dir_path):
        if not is_exist_ok:
            raise FileExistsError("The directory is expected not to exist, but it already does. "
                                  f"Please check the input path: {dir_path}")
        
        # Check directory permissions
        check_directory_permissions(dir_path, mode)
        
        # Check owner permissions
        check_directory_owner(dir_path)
        
        # Check other user permissions
        check_directory_other_permissions(dir_path)
        
    else:
        if mode == 'r' or mode == 'r+':
            raise FileNotFoundError("The directory is expected to exist, but it does not. "
                                    f"Please check the input path: {dir_path}")
        
        # For new directories, check parent directory permissions
        parent_dir = os.path.dirname(dir_path)
        if parent_dir and os.path.exists(parent_dir):
            check_directory_permissions(parent_dir, 'w')
            check_directory_owner(parent_dir)


def safe_listdir(dir_path: str, max_file_num=MAX_DIR_FILES):
    """
    Safely list directory contents
    """
    # First check directory safety
    dir_path = check_directory_path(dir_path, 'r')
    
    filenames = os.listdir(dir_path)
    file_num = len(filenames)
    
    if file_num > max_file_num:
        raise ValueError(f"The number of files in directory is {file_num}, which exceeds the limit {max_file_num}. "
                         f"Please check the directory: {dir_path}")
    
    return filenames


def safe_walk(dir_path: str, max_depth=10, **kwargs):
    """
    Safely walk through directory
    """
    dir_path = check_directory_path(dir_path, 'r', **kwargs)
    
    results = []
    for root, dirs, files in os.walk(dir_path):
        # Check traversal depth
        current_depth = root[len(dir_path):].count(os.sep)
        if current_depth > max_depth:
            del dirs[:]  # Stop further traversal
            continue
        
        # Safety check each subdirectory
        for dir_name in dirs[:]:
            full_dir_path = os.path.join(root, dir_name)
            try:
                full_dir_path = check_directory_path(full_dir_path, 'r')
            except (PermissionError, ValueError) as e:
                logging.warning(f"Skipping directory due to safety check: {full_dir_path}, error: {e}")
                dirs.remove(dir_name)
        
        results.append((root, dirs, files))
    
    return results


def safe_mkdir(dir_path: str, mode=0o750, **kwargs):
    """
    Safely create directory
    """
    parent_dir = os.path.dirname(os.path.abspath(dir_path))
    if parent_dir and parent_dir != dir_path:
        parent_dir = check_directory_path(parent_dir, 'w', **kwargs)
    
    try:
        os.makedirs(dir_path, mode=mode, exist_ok=False)
        logging.info(f"Successfully created directory: {dir_path}")
        return dir_path
    except OSError as e:
        raise OSError(f"Failed to create directory {dir_path}") from e


def safe_rmdir(dir_path: str, **kwargs):
    """
    Safely remove directory
    """
    if not os.path.exists(dir_path):
        return
    parent_dir = os.path.dirname(os.path.abspath(dir_path))
    if parent_dir:
        parent_dir = check_directory_path(parent_dir, 'w', **kwargs)
    try:
        import shutil
        shutil.rmtree(dir_path)
        logging.info(f"Successfully removed directory: {dir_path}")
    except OSError as e:
        raise OSError(f"Failed to remove directory {dir_path}") from e