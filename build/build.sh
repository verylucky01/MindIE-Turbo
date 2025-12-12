#!/bin/bash
# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2024-2025. All rights reserved.
# MindIE is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

set -e
BUILD_DIR=$(dirname $(readlink -f $0))
PROJ_ROOT_DIR=${BUILD_DIR}/..
OUTPUT_DIR=$PROJ_ROOT_DIR/output

function fn_clean() 
{
    echo "Cleaning temporary directories..."
    find ${PROJ_ROOT_DIR}/build/ -mindepth 1 ! -name 'build.sh' -exec rm -rf {} + || true
    rm -rf ${PROJ_ROOT_DIR}/dist
    rm -rf ${PROJ_ROOT_DIR}/mindie_turbo.egg-info
    echo "Temporary directories cleaned!"
}

function fn_main()
{
    local release=false
    for arg in "$@"; do
        if [ "$arg" = "release" ]; then
            release=true
            break
        fi
    done

    if [ ! -d "$OUTPUT_DIR" ]; then
        mkdir -p $OUTPUT_DIR
    fi

    cd ${PROJ_ROOT_DIR}
    fn_clean
    MINDIE_TURBO_VERSION="1.0.RC1"
    if [ ! -f "${PROJ_ROOT_DIR}"/../CI/config/version.ini ]; then
        echo "version.ini does not exist!"
    else
        MINDIE_TURBO_VERSION=$(cat ${PROJ_ROOT_DIR}/../CI/config/version.ini | grep "PackageName" | cut -d "=" -f 2)
    fi

    if [[ "$MINDIE_TURBO_VERSION" =~ RC[0-9]+$ ]]; then
        MINDIE_TURBO_WHEEL_VERSION=$(echo $MINDIE_TURBO_VERSION | sed -E 's/([0-9]+)\.([0-9]+)\.RC([0-9]+)/\1.\2rc\3/')
    else
        MINDIE_TURBO_WHEEL_VERSION=$(echo $MINDIE_TURBO_VERSION | sed -E 's/([0-9]+)\.([0-9]+)\.RC([0-9]+)\.([0-9]+)/\1.\2rc\3.post\4/')
    fi
    MINDIE_TURBO_WHEEL_VERSION=$(echo $MINDIE_TURBO_WHEEL_VERSION | sed -s 's!.T!.alpha!')
    echo "Final MINDIE_TURBO_WHEEL_VERSION: $MINDIE_TURBO_WHEEL_VERSION"

    MINDIE_TURBO_WHEEL_VERSION="${MINDIE_TURBO_WHEEL_VERSION}" python3 ${PROJ_ROOT_DIR}/setup.py bdist_wheel

    cd $OUTPUT_DIR
    rm -rf $OUTPUT_DIR/*
    WHL_FILENAME=$(ls ${PROJ_ROOT_DIR}/dist/mindie*.whl)
    PYTHON_VERSION=$(echo $WHL_FILENAME | sed -E 's/.*-(cp[0-9]+)-.*/\1/' | sed 's/^cp/py/')
    ARCHITECTURE=$(echo $WHL_FILENAME | sed -E 's/.*-(linux_[a-z0-9_]+).*/\1/')
    TAR_PACKAGE_NAME="Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}.tar.gz"

    mkdir -p $OUTPUT_DIR/Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}

    if [ $release = true ]; then
        mkdir -p $PROJ_ROOT_DIR/tmp
        cp ${PROJ_ROOT_DIR}/dist/mindie*.whl $PROJ_ROOT_DIR/tmp
        cp ${PROJ_ROOT_DIR}/requirements.txt $PROJ_ROOT_DIR/tmp
        cd $BUILD_DIR/../../CI/script/
        sh ./signature.sh cms
        cd -
        cp $PROJ_ROOT_DIR/tmp/* ./Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}
        rm -rf $PROJ_ROOT_DIR/tmp
    else 
        cp ${PROJ_ROOT_DIR}/dist/mindie*.whl ./Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}
        cp ${PROJ_ROOT_DIR}/requirements.txt ./Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}
    fi

    tar czf $TAR_PACKAGE_NAME ./Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE} --owner=0 --group=0
    rm -rf ./Ascend-mindie-turbo_${MINDIE_TURBO_VERSION}_${PYTHON_VERSION}_${ARCHITECTURE}

    echo "Created tar.gz file: $TAR_PACKAGE_NAME"
    cd ${PROJ_ROOT_DIR}
    fn_clean
}

fn_main "$@"
