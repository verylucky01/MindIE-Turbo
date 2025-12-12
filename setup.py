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

import io
import re
import logging
import os
import platform
import shutil
import importlib
import sys
from pathlib import Path
from typing import List

from setuptools import setup, find_packages

from setuptools.command.install import install
from setuptools.command.develop import develop

from mindie_turbo.utils.file_utils import safe_open, check_file_path
from mindie_turbo.utils.directory_utils import safe_listdir, check_directory_path


ROOT_DIR = os.path.dirname(__file__)


DEFAULT_ALLOWED_DIRS = [
    Path(ROOT_DIR),
    Path(ROOT_DIR) / "mindie_turbo",
]


def load_module_from_path(module_name, path, allowed_dirs=None):
    if allowed_dirs is None:
        allowed_dirs = DEFAULT_ALLOWED_DIRS
        
    path = check_file_path(path)
    file_path = Path(path).resolve()
    
    is_allowed = any(file_path.is_relative_to(allowed_dir.resolve()) for allowed_dir in allowed_dirs)
    if not is_allowed:
        raise ValueError(f"Module path {path} is not in allowed directories. ")
    if not file_path.exists():
        raise FileNotFoundError(f"Module file does not exist: {file_path}")
    if file_path.suffix != '.py':
        raise ValueError(f"Invalid module file extension: {file_path.suffix}. Expected .py")
    
    
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def get_path(*filepath) -> str:
    """Get the path joined with the project root directory."""
    return os.path.join(ROOT_DIR, *filepath)


def read_readme() -> str:
    """Read the README file."""
    readme_path = get_path("README.md")
    readme_path = check_file_path(readme_path)
    return io.open(readme_path, "r", encoding="utf-8").read()


def get_requirements() -> List[str]:
    """Get Python package dependencies from requirements.txt."""
    try:
        with safe_open(get_path("requirements.txt")) as f:
            requirements = f.read().strip().split("\n")
        return requirements
    except FileNotFoundError as e:
        raise FileNotFoundError("Requirements file not found") from e
    except PermissionError as e:
        raise PermissionError("No permission to read requirements file") from e
    except IsADirectoryError as e:
        raise IsADirectoryError("Requirements path points to a directory") from e


def get_version() -> str:
    """Return the version of MindIE Turbo, from mindie_turbo/version.py"""
    # Check environment variable version
    version_pattern = r'^[0-9]+\.[0-9]+\.([0-9]+|[a-zA-Z]*[0-9]+)$'
    # Get base version
    version_file_path = os.path.join(ROOT_DIR, "mindie_turbo", "version.py")
    version_file_path = check_file_path(version_file_path)
    spec = importlib.util.spec_from_file_location("version", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    mindie_turbo_version = version_module.__version__
    
    # Check and process version.ini file
    version_ini_path = os.path.join(ROOT_DIR, "../CI/config/version.ini")
    if os.path.isfile(version_ini_path):
        mindie_turbo_version = _read_version_from_ini(version_ini_path, mindie_turbo_version, version_pattern)
    else:
        logging.info(f"version.ini does not exist! Using version tag: {mindie_turbo_version}")
    
    # Process version string format
    if re.search(r'RC[0-9]+$', mindie_turbo_version):
        mindie_turbo_wheel_version = re.sub(
            r'([0-9]+)\.([0-9]+)\.RC([0-9]+)',
            r'\1.\2rc\3',
            mindie_turbo_version
        )
    else:
        mindie_turbo_wheel_version = re.sub(
            r'([0-9]+)\.([0-9]+)\.RC([0-9]+)\.([0-9]+)',
            r'\1.\2rc\3.post\4',
            mindie_turbo_version
        )

    mindie_turbo_wheel_version = mindie_turbo_wheel_version.replace(".T", ".alpha")
    logging.info(f"Final version tag: {mindie_turbo_wheel_version}")
    return mindie_turbo_wheel_version


def _read_version_from_ini(version_ini_path, default_version, version_pattern):
    """Read version from version.ini file"""
    with safe_open(version_ini_path, 'r') as f:
        for line in f:
            if line.startswith("PackageName"):
                target_version = line.split("=", 1)[1].strip()
                if re.match(version_pattern, target_version):
                    return target_version
    return default_version


class CustomInstall(install):
    def run(self):
        self.distribution.editable_mode = False
        install.run(self)


class CustomDevelop(develop):
    def run(self):
        self.distribution.editable_mode = True
        develop.run(self)


def get_wheel_tag():
    """Return the Python version and architecture tag for the wheel file."""
    python_version = sys.version_info
    python_version_str = f"cp{python_version[0]}{python_version[1]}"

    system_arch = platform.machine()
    system_platform = platform.system().lower()

    if system_platform == "linux":
        if system_arch == "x86_64":
            arch = "x86_64"
        elif system_arch == "aarch64":
            arch = "aarch64"
        else:
            raise RuntimeError(f"Unsupported system architecture: {system_arch}")
    else:
        raise RuntimeError(f"Unsupported system platform: {system_platform}")

    return python_version_str, arch


def rename_wheel_file():
    """Rename the generated wheel file based on the Python version and architecture tag."""
    dist_dir = get_path("dist")
    wheel_files = [f for f in safe_listdir(dist_dir) if f.endswith(".whl")]

    if not wheel_files:
        raise RuntimeError("No wheel files!")

    wheel_file = wheel_files[0]
    python_version_str, arch = get_wheel_tag()

    new_wheel_name = f"mindie_turbo-{get_version()}-{python_version_str}-{python_version_str}-linux_{arch}.whl"
    old_wheel_path = os.path.join(dist_dir, wheel_file)
    new_wheel_path = os.path.join(dist_dir, new_wheel_name)

    if not os.path.exists(old_wheel_path):
        raise FileNotFoundError(f"Source wheel file not found: {old_wheel_path}")

    if not os.path.isfile(old_wheel_path):
        raise ValueError(f"Source path is not a file: {old_wheel_path}")

    if os.path.exists(new_wheel_path):
        logging.warning(f"Target file already exists: {new_wheel_path}")
        os.remove(new_wheel_path)

    if not os.access(dist_dir, os.W_OK):
        raise PermissionError(f"No write permission for directory: {dist_dir}")

    try:
        os.rename(old_wheel_path, new_wheel_path)
        logging.info(f"Successfully renamed {wheel_file} to {new_wheel_name}")
        
    except OSError as e:
        if e.errno == 18:
            logging.info("Cross-device rename detected, using copy+delete method")
            shutil.copy2(old_wheel_path, new_wheel_path)
            os.remove(old_wheel_path)
            logging.info(f"Copied and removed original file: {new_wheel_name}")
        else:
            raise RuntimeError(f"Failed to rename wheel file: {e}") from e


def safe_remove(path, max_retries=3, delay=1):
    """Safely remove a directory with retry mechanism and error handling.
    
    This function attempts to remove a directory and handles common issues
    such as permission errors, file locks, and temporary system conflicts
    by implementing a retry mechanism with configurable delays.
    
    Parameters:
        path (str): The file system path to the directory to be removed.
        max_retries (int): Maximum number of retry attempts (default: 3).
        delay (float): Delay in seconds between retry attempts (default: 1).
        
    Returns:
        bool: True if the directory was successfully removed, False otherwise.
        
    Raises:
        ValueError: If the provided path is not a valid string.
        TypeError: If max_retries or delay are not numeric values.
    """
    import time
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                logging.info(f"Successfully removed: {path}")
                return True
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed to remove {path}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logging.error(f"Failed to remove {path} after {max_retries} attempts")
                return False
    return True


def pack_wheel_file():
    """Pack built wheel file into a compressed file with tar.gz format"""
    dist_dir = get_path("dist")
    dist_dir = check_directory_path(dist_dir)
    output_dir = get_path("output")
    
    # Clean up output directory
    if os.path.exists(output_dir):
        if not safe_remove(output_dir):
            logging.error(f"Failed to remove output directory: {output_dir}")
    
    # Create output directory
    try:
        os.mkdir(output_dir, mode=0o750)
    except OSError as e:
        logging.error(f"Failed to create output directory {output_dir}: {e}")

    # Get wheel files
    wheel_files = [f for f in safe_listdir(dist_dir) if f.endswith(".whl")]
    if not wheel_files:
        logging.error("No wheel files found in dist directory")

    wheel_file = wheel_files[0]
    wheel_file_path = os.path.join(dist_dir, wheel_file)
    python_version_str, arch = get_wheel_tag()

    # Create package directory structure
    package_name = f"Ascend-mindie-turbo_{get_version()}_{python_version_str}_{arch}"
    tar_file_name = package_name + ".tar.gz"
    package_path = os.path.join(output_dir, package_name)
    
    try:
        os.mkdir(package_path, mode=0o750)
    except OSError as e:
        logging.error(f"Failed to create package directory {package_path}: {e}")

    # Copy files to package directory
    try:
        wheel_file_path = check_file_path(wheel_file_path)
        shutil.copy(wheel_file_path, package_path)
        shutil.copy(check_file_path(os.path.join(ROOT_DIR, "requirements.txt")), package_path)
    except (IOError, OSError) as e:
        logging.error(f"Failed to copy files to package directory: {e}")
        safe_remove(package_path)  # Clean up partially created directory

    # Create compressed archive
    try:
        shutil.make_archive(
            base_name=package_path,
            format="gztar",
            root_dir=package_path,
        )
    except (IOError, OSError) as e:
        logging.error(f"Failed to create archive: {e}")
        safe_remove(package_path)  # Clean up partially created directory

    # Clean up temporary package directory
    if not safe_remove(package_path):
        logging.warning(f"Failed to remove temporary package directory: {package_path}")
        # Option to continue returning success since archive was created successfully
        # or return failure, depending on business requirements
    
    logging.info(f"Successfully created package: {tar_file_name}")


setup(
    name="mindie_turbo",
    version=get_version(),
    author="Alan",
    license="Apache 2.0",
    description=(
        "MindIE Turbo: An LLM inference acceleration framework featuring extensive plugin collections optimized "
        "for NPU devices."
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    cmdclass={
        "install": CustomInstall,
        "develop": CustomDevelop,
    },
    url="",
    project_urls={
        "Homepage": "",
        "Documentation": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(exclude=("examples", "tests", "csrc")),
    python_requires=">=3.9",
    install_requires=get_requirements(),
)

# Restricted by the version of setuptools on CI conatiner, we have to manually rename the wheel file instead of
# overriding the get_tag function of setuptools.command.bdist_wheel.bdist_wheel
if "bdist_wheel" in sys.argv:
    rename_wheel_file()
    pack_wheel_file()