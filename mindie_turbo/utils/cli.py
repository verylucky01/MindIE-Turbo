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

from dataclasses import dataclass
from typing import List
import argparse
import warnings


@dataclass
class BaseConfig:
    """Base configuration for MindIE-Turbo.

    Contains basic settings that are required for all running modes.
    """

    # Add more basic settings here

    def validate(self) -> None:
        # Add validation logic here
        pass


def parse_custom_args(args: argparse.Namespace, unknown: List[str]) -> argparse.Namespace:
    """Parse unknown command line arguments into namespace.

    Args:
        args: Existing argument namespace to update.
        unknown: List of unknown arguments in format ['--key', 'value', ...].

    Returns:
        Updated argument namespace.

    Warns:
        UserWarning: When unknown arguments are detected.
    """
    if unknown:
        warnings.warn(f"\n\n\nDetected unknown arguments: {unknown}\n\n\n", UserWarning)
        
    if not isinstance(unknown, list):
        raise TypeError("unknown must be a list")

    for i, item in enumerate(unknown):
        if not isinstance(item, str):
            raise TypeError(f"All unknown arguments must be strings, got {type(item)} at index {i}")

    i = 0
    while i < len(unknown):
        arg = unknown[i]
        
        if arg.startswith("--"):
            key = _extract_and_validate_key(arg)
            if key is None:
                i += 1
                continue
            
            values = []
            i += 1
            
            while i < len(unknown) and not unknown[i].startswith("--"):
                values.append(unknown[i])
                i += 1
            
            # Unified handling of return value types
            converted_values = _convert_values_to_appropriate_type(values)
            if isinstance(converted_values, list) and len(converted_values) == 1:
                value = converted_values[0]  # Single value case
            else:
                value = converted_values  # Multiple values or empty value case
                
            _safe_set_attribute(args, key, value)
        else:
            warnings.warn(f"Skipping malformed argument: {arg}", UserWarning)
            i += 1

    return args


def _extract_and_validate_key(arg: str):
    """Extract and validate key name from argument string."""
    key = arg[2:].replace("-", "_")
    
    if not key.isidentifier():
        warnings.warn(f"Invalid argument name: '{key}', skipping", UserWarning)
        return None
    
    return key


def _convert_values_to_appropriate_type(values: List[str]):
    """Convert string values to appropriate Python types. Always returns a list."""
    if not values:
        return [True]  # Flag argument without value, always return list
    
    if len(values) == 1:
        return [_convert_single_value(values[0])]  # Single value also returns list
    
    return _convert_multiple_values(values)  # Multiple values return list


def _convert_single_value(value: str):
    """Convert a single string value to appropriate type."""
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    elif value.isdigit():
        return int(value)
    elif _is_float(value):
        return float(value)
    else:
        return value


def _convert_multiple_values(values: List[str]):
    """Convert multiple string values to appropriate types."""
    return [_convert_single_value(value) for value in values]


def _safe_set_attribute(args: argparse.Namespace, key: str, value):
    """Safely set attribute on namespace with validation."""
    if hasattr(args, key):
        warnings.warn(f"Argument '{key}' already exists in namespace, overwriting", UserWarning)
    
    setattr(args, key, value)


def _is_float(value: str) -> bool:
    """Check if a string can be converted to float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def create_parser() -> argparse.ArgumentParser:
    """Creates argument parser with basic settings.

    Returns:
        Configured argument parser.

    Example:
    args, unknown_args = parser.parse_known_args()
    parse_custom_args(args, unknown_args)

    An example of adding a new argument:
    group = parser.add_argument_group(title="basic_settings")
    group.add_argument(
        '--backend-type',
        type=int,
        default=BaseConfig.backend_type,
        choices=[0, 1],
        help='Backend type: 0 for MindIE mode, 1 for Turbo mode'
    )
    """
    arg_parser = argparse.ArgumentParser(conflict_handler="resolve")
    return arg_parser

parser = create_parser()
