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
from typing import Optional

from mindie_turbo.adaptor.base_turbo import BaseTurbo, TurboPatch, validate_optimization_level
from mindie_turbo.utils.logger import logger

DECORATE = "decorate"


class VLLMTurbo(BaseTurbo):
    """VLLM specific Turbo optimization implementation."""

    def check_environment(self) -> None:
        try:
            import torch_npu
        except ImportError as e:
            raise RuntimeError(
                "Failed to import torch_npu, please install it first."
            ) from e

    def setup_environment(self) -> None:
        pass

    def register_patches(self, level: int) -> None:
        """Register vLLM specific optimization patches."""
        if level >= 0:
            pass

        if level >= 1:
            pass

        if level >= 2:
            pass

        if level >= 3:
            pass

    def register_extra_patches(self) -> None:
        """Register extra patches that are not activated when import vllm_turbo"""
        pass

    def register_env_patches(self) -> None:
        pass

    def activate_extra_patches(self, patch_type: str) -> None:
        """Activate patches according to given patch types.

        Args:
            patch_type: Which type of patches to be activated.
        """
        if patch_type not in self.extra_patch_mapping:
            raise ValueError(
                f"Unsupported patch_type: {patch_type}, available patch_type are {self.extra_patch_mapping.keys()}"
            )

        for target in self.extra_patch_mapping[patch_type]:
            self.patcher.patches[target].apply_patch()


def get_validated_optimization_level() -> int:
    """
    Safely get and validate VLLM_OPTIMIZATION_LEVEL environment variable.
    
    Returns:
        Validated optimization level between 0 and 3
        
    Raises:
        ValueError: If environment variable is invalid
    """
    env_value = os.getenv("VLLM_OPTIMIZATION_LEVEL", "2")
    
    validated_level = validate_optimization_level(env_value)
    
    return validated_level


def initialize_vllm_turbo() -> Optional[VLLMTurbo]:
    """
    Safely initialize VLLM Turbo with environment variable validation.
    
    Returns:
        Initialized VLLMTurbo instance or None if initialization fails
    """
    try:
        # Get and validate optimization level
        optimization_level = get_validated_optimization_level()
        
        # Initialize turbo
        turbo = VLLMTurbo()
        turbo.activate(optimization_level)
        turbo.register_extra_patches()
        
        logger.info(f"vLLM Turbo activated with optimization level: {optimization_level}")
        return turbo
        
    except ValueError as e:
        logger.error(f"Failed to initialize vLLM Turbo due to invalid configuration: {e}")
        logger.warning("Falling back to default optimization level 2")
        
        # Fallback to default
        try:
            turbo = VLLMTurbo()
            turbo.activate(2)  # Default fallback
            turbo.register_extra_patches()
            logger.info("vLLM Turbo activated with fallback level: 2")
            return turbo
        except Exception as fallback_error:
            logger.error(f"Fallback initialization also failed: {fallback_error}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize vLLM Turbo: {e}")
        return None


# Create global instance with safe initialization
vllm_turbo = initialize_vllm_turbo()

if vllm_turbo:
    TurboPatch.set_frontend(vllm_turbo)
else:
    logger.warning("vLLM Turbo initialization failed. Running without optimizations.")
