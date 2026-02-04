# README

## 简介

MindIE Turbo 是基于 NPU 芯片的大语言模型推理引擎加速插件库，旨在承载自研的大语言模型优化算法及推理引擎相关优化。MindIE Turbo 提供一系列模块化和插件化接口，支持外部推理引擎的接入和加速。

以下是两个 MindIE-Turbo 代码仓库**智能体**，只需点击 "**Ask AI**" 徽章，即可进入其专属页面，有效缓解源码阅读的困难，开启智能代码学习与问答体验！它们将帮助您更深入地理解 MindIE-Turbo 的运行原理，并协助解决使用过程中遇到的问题与错误。


<div align="center">

[![Zread](https://img.shields.io/badge/Zread-Ask_AI-_.svg?style=flat&color=0052D9&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/verylucky01/MindIE-Turbo)&nbsp;&nbsp;&nbsp;&nbsp;
[![DeepWiki](https://img.shields.io/badge/DeepWiki-Ask_AI-_.svg?style=flat&color=0052D9&labelColor=000000&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==)](https://deepwiki.com/verylucky01/MindIE-Turbo)

</div>

目前，MindIE Turbo 已支持 vLLM 的适配。通过与 vLLM 和 vLLM Ascend 的对接，能够提供更强的性能和更多的推理优化算法。在实际使用中，用户只需在对应的 Python 环境中安装 MindIE Turbo，系统会自动检测 vLLM 并启用优化，无需修改代码即可完成性能提升。

## 会议日历

-   11/30/2025：MindIE Turbo 正式宣布开源并面向公众开放！
-   11/30/2025: We are excited to announce that MindIE Turbo is now open source and available to the public!

## 支持框架

**vLLM**：vLLM 是伯克利大学 LMSYS 组织开源的大语言模型高速推理框架，旨在极大地提升实时场景下的语言模型服务的吞吐率与内存使用率，提供易用、快速、便宜的 LLM 服务。

## 架构说明
MindIE-Turbo 主要包含以下模块（部分为预留模块）:

- adaptor: 适配不同推理框架的优化实现
  - vllm: vLLM 框架适配
- utils: 通用工具

## 环境准备

### 硬件环境及操作系统准备

- 目前 MindIE Turbo 支持的硬件环境：A800I A2 推理产品（32GB/64GB）
- 支持的操作系统请参见《MindIE 安装指南》中 "环境准备 > 支持的操作系统" 章节

### 开发环境准备

在安装 MindIE Turbo 之前请检查以下组件的配套关系和安装情况：

<!-- 表格标题：组件配套驱动与固件（HDK） -->

| 组件         | 配套版本            | 获取链接       |
| ------------ | ------------------- | -------------- |
| **驱动与固件（HDK）** | >=24.0             | [获取链接](https://support.huawei.com/enterprise/zh/ascend-computing/ascend-hdk-pid-252764743/software)       |
| **CANN**     | >=8.0.0             | [获取链接](https://www.hiascend.com/developer/download/community/result?module=ie%2Bpt%2Bcann)      |
| **PyTorch**  | 2.5.1               | [获取链接](https://www.hiascend.com/developer/download/community/result?module=ie%2Bpt%2Bcann)       |
| **Python**   | 3.10.x、3.11.x      | -              |

1. 安装配套版本的驱动与固件（HDK）、CANN 软件（Toolkit、Kernels 和 NNAL）请参考《CANN 软件安装指南》，在 "选择安装场景" 页面，按下列指引选择：
- **安装方式**: 在物理机上安装
- **操作系统**: 根据实际情况选择
- **业务场景**: 选择训练 & 推理 & 开发调试

2. 安装 PyTorch，请参考组件[安装 PyTorch 框架](https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0005.html)与[安装 torch_npu 插件](https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0006.html)安装

## 使用说明

### 1. 安装指南

1. 联系相关人员获取 MindIE Turbo 软件包。

2. 将 MindIE Turbo 软件包上传到安装环境的任意路径（例如：`/home/package`）。

3. 进入软件包所在路径：

   ```bash
   cd /home/package
   ```
4. 执行以下命令安装 MindIE Turbo：
   ```bash
   python setup.py install
   ```
5. 返回上级目录，执行以下命令验证是否安装成功：
   ```bash
   cd ../
   pip show mindie_turbo
   ```
   如果出现如下示例结果，表示安装成功：
   ```bash
   Version: 1.0rc1
   Summary: MindIE Turbo: An LLM inference acceleration framework featuring extensive plugin collections optimized for NPU devices.
   Home-page:
   Author-email:
   License: Apache 2.0
   Location: /usr/local/lib/python3.11/site-packages
   Requires:
   Required-by:
   ```

### 2. 快速使用

MindIE Turbo 不会修改任何使用行为，与原有框架保持一致，使得用户可以很轻松地应用并迁移项目。以 vLLM 框架为例：

1. 安装 vLLM 与 vLLM Ascend。

   请参考 [vLLM Ascend 安装文档](https://vllm-ascend.readthedocs.io/en/latest/installation.html)进行安装。

2. 根据需要，进行离线批量推理或在线服务推理。

- 离线批量推理
   请参考 [vLLM 离线推理示例文档](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#offline-batched-inference)进行推理。以下为最简单的示例（来自 [vllm/examples/offline_inference/basic/basic.py](https://github.com/vllm-project/vllm/blob/main/examples/offline_inference/basic/basic.py)），请根据需要修改：
   ```python
   from vllm import LLM, SamplingParams

   # Sample prompts.
   prompts = [
      "Hello, my name is",
      "The president of the United States is",
      "The capital of France is",
      "The future of AI is",
   ]
   # Create a sampling params object.
   sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

   # Create an LLM.
   llm = LLM(model="facebook/opt-125m")
   # Generate texts from the prompts. The output is a list of RequestOutput objects
   # that contain the prompt, generated text, and other information.
   outputs = llm.generate(prompts, sampling_params)
   # Print the outputs.
   for output in outputs:
      prompt = output.prompt
      generated_text = output.outputs[0].text
      print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
   ```
- 启动在线推理服务
请根据 [vLLM 在线服务示例文档](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)启动服务。以下以 Qwen2.5-1.5B-Instruct 简单示例，请根据需要修改：
   ```bash
   vllm serve Qwen/Qwen2.5-1.5B-Instruct
   ```

## 性能调优

### 1. 服务器性能调优

使用服务器进行大模型推理时，建议开启 CPU 高性能模式以及透明大页，开启后可提升性能与稳定性。

步骤一：安装开启 CPU 高性能模式所需的相关库。
```
apt-get install cpufrequtils
apt install linux-tools-common linux-tools-$(uname -r)
```

步骤二：使用 cpupower 指令设置高性能模式。
```
cpupower frequency-set -g performance
```

步骤三：开启透明大页，提升性能稳定性。
```
echo always > /sys/kernel/mm/transparent_hugepage/enabled
```

### 2. 性能调优相关环境变量
- VLLM_OPTIMIZATION_LEVEL
  - 设置 vLLM 推理引擎的优化级别，用于控制 vLLM 的性能优化程度，数值越高优化越激进。
  - 取值范围为 0-3，默认为 2：
    - 0: 禁用大部分优化，用于调试
    - 1: 基础优化级别
    - 2: 中等优化级别（推荐）
    - 3: 最高优化级别，可能包含实验性功能

## 支持特性

## 参与贡献

1. Fork 本仓库
2. 新建分支
3. 验证修改
4. 提交代码
5. 新建 Pull Request
