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

import logging
import logging.handlers
import os
import shutil
from typing import Optional

from mindie_turbo.utils.file_utils import check_file_path
from mindie_turbo.utils.directory_utils import check_directory_path


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    fmt: str = "%(levelname)-8s - %(asctime)s - PID:%(process)d - "
               "%(threadName)s - %(filename)s:%(lineno)d - %(message)s"
) -> logging.Logger:
    """Set up and configure a logger with comprehensive validation.
    
    Args:
        name: Logger name to identify the logger instance.
        log_file: Optional path to log file. If provided, logs will be written to file.
        level: Logging level (default: logging.INFO).
        fmt: Log message format string.
    
    Returns:
        Configured logger instance.
    
    Raises:
        PermissionError: If insufficient permissions for log file/directory.
        OSError: If there are issues creating the log directory or file.
        DiskSpaceError: If insufficient disk space.
    """
    # Validate log file permissions if provided
    if log_file:
        log_file = os.path.expanduser(log_file)
    max_file_size = 10 * 1024 * 1024
    backup_count = 5
    
    if log_file:
        _validate_log_configuration(log_file, max_file_size)
    
    # Create formatter
    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Get or create logger
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger_instance.handlers.clear()
    
    # Create and add stream handler (console output)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger_instance.addHandler(stream_handler)
    
    # Create and add file handler if log_file is provided
    if log_file:
        try:
            # Use RotatingFileHandler for log rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, 
                maxBytes=max_file_size, 
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger_instance.addHandler(file_handler)
        except Exception as e:
            # Fallback to basic file handler if rotation fails
            logging.warning(f"RotatingFileHandler failed: {e}, using basic FileHandler")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger_instance.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger_instance.propagate = False
    
    return logger_instance


def _validate_log_configuration(log_file: str, required_space: int = 10 * 1024 * 1024) -> None:
    """Comprehensive validation of log file configuration.
    
    Args:
        log_file: Path to the log file.
        required_space: Minimum required disk space in bytes.
    
    Raises:
        PermissionError: If insufficient permissions.
        OSError: For file system related errors.
        DiskSpaceError: If insufficient disk space.
    """
    log_dir = os.path.dirname(os.path.abspath(log_file)) or '.'
    
    # 1. Check and create directory with proper permissions
    _validate_directory(log_dir)
    
    # 2. Check file permissions and ownership
    if os.path.exists(log_file):
        log_file = check_file_path(log_file, mode='r+')
    
    # 3. Check disk space
    _check_disk_space(log_dir, required_space)


def _validate_directory(log_dir: str) -> None:
    """Validate directory permissions and ownership."""
    # Check if directory exists, create if needed
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, mode=0o750, exist_ok=True)
        except OSError as e:
            raise OSError(f"Cannot create log directory '{log_dir}': {e}") from e
    
    log_dir = check_directory_path(log_dir, mode='r+')


def _check_disk_space(log_dir: str, required_space: int) -> None:
    """Check if there's sufficient disk space for logging."""
    try:
        disk_usage = shutil.disk_usage(log_dir)
        available_space = disk_usage.free
        
        if available_space < required_space:
            raise DiskSpaceError(
                f"Insufficient disk space in '{log_dir}'. "
                f"Available: {available_space // (1024*1024)}MB, "
                f"Required: {required_space // (1024*1024)}MB"
            )
        
        # Warn if space is getting low
        if available_space < 5 * required_space:  # Less than 5x required space
            logging.warning(
                f"Low disk space in '{log_dir}': {available_space // (1024*1024)}MB available"
            )
            
    except OSError as e:
        raise OSError(f"Cannot check disk space for '{log_dir}': {e}") from e


class DiskSpaceError(Exception):
    """Exception raised for insufficient disk space."""
    pass


# Configure logger with enhanced validation
logger = setup_logger(
    name="MindIE-Turbo",
    log_file="~/mindie/Turbo.log",
    level=logging.ERROR,
    fmt="%(levelname)-8s - %(asctime)s - PID:%(process)d - %(threadName)s - %(filename)s:%(lineno)d - %(message)s"
)