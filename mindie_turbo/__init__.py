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

"""
MindIE Turbo: An LLM inference acceleration framework featuring extensive plugin collections optimized for 
NPU devices.
"""
__all__ = [
    "vllm_turbo",
]


import os
import stat
from pathlib import Path


# Determine whether other regular users have write permissions to the directory
parnet_dir = Path(__file__).parent.absolute()

if (os.stat(parnet_dir).st_mode & stat.S_IWOTH):
    raise PermissionError(f"Other regular users in the current directory [{parnet_dir}] have write permissions\n")