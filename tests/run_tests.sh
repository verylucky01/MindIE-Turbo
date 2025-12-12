#!/bin/bash
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

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$PROJECT_ROOT/tests"
COVERAGE_DIR="$PROJECT_ROOT/coverage_report"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$COVERAGE_DIR"

echo -e "${BLUE}🚀 开始运行单元测试并统计覆盖率...${NC}"
echo -e "${YELLOW}项目根目录: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}测试目录: $TESTS_DIR${NC}"
echo

check_dependencies() {
    if ! python -c "import coverage" &>/dev/null; then
        echo -e "${YELLOW}安装 coverage 包...${NC}"
        pip install coverage
    fi
    
    if ! python -c "import pytest" &>/dev/null; then
        echo -e "${YELLOW}安装 pytest 包...${NC}"
        pip install pytest
    fi
}

run_coverage_tests() {
    echo -e "${BLUE}📊 运行测试并生成覆盖率报告...${NC}"
    
    coverage erase
    
    coverage run --source=mindie_turbo -m pytest \
        "$TESTS_DIR/adaptor/" \
        "$TESTS_DIR/utils/" \
        -v \
        --tb=short \
        --junitxml="$COVERAGE_DIR/test_results_$TIMESTAMP.xml"
    
    echo -e "\n${BLUE}📈 生成覆盖率报告...${NC}"
    coverage report -m --omit="*/test*" > "$COVERAGE_DIR/coverage_report_$TIMESTAMP.txt"
    coverage html -d "$COVERAGE_DIR/html_$TIMESTAMP" --omit="*/test*"
    coverage xml -o "$COVERAGE_DIR/coverage_$TIMESTAMP.xml" --omit="*/test*"
    
    echo -e "\n${GREEN}✅ 覆盖率摘要:${NC}"
    coverage report --omit="*/test*" | grep -E "(TOTAL|mindie_turbo)"
}

run_specific_tests() {
    local test_dir=$1
    echo -e "${BLUE}🧪 运行 $test_dir 测试...${NC}"
    
    coverage run --source=mindie_turbo -m pytest \
        "$TESTS_DIR/$test_dir/" \
        -v \
        --tb=short
}

show_summary() {
    echo -e "\n${GREEN}🎉 测试完成!${NC}"
    echo -e "${BLUE}📁 覆盖率报告保存在:${NC}"
    echo -e "  📄 文本报告: $COVERAGE_DIR/coverage_report_$TIMESTAMP.txt"
    echo -e "  🌐 HTML报告: $COVERAGE_DIR/html_$TIMESTAMP/index.html"
    echo -e "  📊 XML报告: $COVERAGE_DIR/coverage_$TIMESTAMP.xml"
    echo -e "  ⚡ JUnit结果: $COVERAGE_DIR/test_results_$TIMESTAMP.xml"
}

main() {
    check_dependencies
    
    echo -e "${BLUE}🔍 发现以下测试文件:${NC}"
    find "$TESTS_DIR" -name "test_*.py" | while read file; do
        echo -e "  📋 $(basename "$file")"
    done
    
    echo
    echo -e "${YELLOW}找到 $(find "$TESTS_DIR" -name "test_*.py" | wc -l) 个测试文件${NC}"
    
    run_coverage_tests
    
    show_summary
    
    if command -v open &>/dev/null; then
        open "$COVERAGE_DIR/html_$TIMESTAMP/index.html"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$COVERAGE_DIR/html_$TIMESTAMP/index.html"
    fi
}

case "${1:-}" in
    "adaptor")
        run_specific_tests "adaptor"
        ;;
    "utils")
        run_specific_tests "utils"
        ;;
    "help"|"-h"|"--help")
        echo -e "${GREEN}使用方法:${NC}"
        echo -e "  $0           - 运行所有测试并生成覆盖率报告"
        echo -e "  $0 adaptor   - 只运行 adaptor 测试"
        echo -e "  $0 utils     - 只运行 utils 测试"
        echo -e "  $0 help      - 显示帮助信息"
        ;;
    *)
        main
        ;;
esac