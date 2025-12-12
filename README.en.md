
# README

## Introduction
MindIE Turbo is a large language model inference engine acceleration plugin library. It is designed to incorporate self-developed large language model optimization algorithms and inference engine-related optimizations. MindIE Turbo provides a series of modular and plugin-based interfaces, supporting the integration and acceleration of external inference engines.

Currently, MindIE Turbo has enabled adaptation for vLLM. By interfacing with vLLM and vLLM-Ascend, it delivers stronger performance and more inference optimization algorithms. In practical use, users only need to install MindIE Turbo in the corresponding Python environment. The system will automatically detect vLLM and enable optimizations, achieving performance improvements without requiring any code modifications.

## Meeting Schedule

-   11/30/2025: We are excited to announce that MindIE Turbo is now open source and available to the public!

## Supported Frameworks:
**vLLM**: vLLM is an open-source large language model inference framework developed by the LMSYS group at the University of California, Berkeley. It aims to greatly improve the throughput and memory efficiency of LLM services in real-time scenarios, providing easy-to-use, fast, and cost-effective LLM services. MindIE Turbo has been integrated with vLLM-Ascend to enable inference acceleration seamlessly within the vLLM framework.

## Architecture Overview
MindIE-Turbo consists of the following modules (some of which are reserved for future functionality):

- adaptor: Optimized implementation for different inference frameworks
  - vllm: vLLM framework adaptation
- utils: General utilities

## Environment Setup
### Hardware and Operating System Requirements
- The hardware environments supported by MindIE Turbo include: A800I A2  (32GB/64GB)
- Supported operating systems can be found in the "Environment Setup > Supported Operating Systems" section of the "MindIE Installation Guide"

### Development Environment Setup
Before installing MindIE Turbo, please check the following component compatibility and installation status:

<!-- Table title: Component Compatibility and Firmware (HDK) -->

| Component               | Required Version      | Download Link                                                       |
|-------------------------|-----------------------|---------------------------------------------------------------------|
| **Driver and Firmware (HDK)** | >=24.0                | [Download Link](https://support.huawei.com/enterprise/zh/ascend-computing/ascend-hdk-pid-252764743/software)  |
| **CANN**                 | >=8.0.0               | [Download Link](https://www.hiascend.com/developer/download/community/result?module=ie%2Bpt%2Bcann)     |
| **PyTorch**              | 2.5.1                 | [Download Link](https://www.hiascend.com/developer/download/community/result?module=ie%2Bpt%2Bcann)     |
| **Python**               | 3.10.x, 3.11.x        | -                                                                   |

1. To install the required driver and firmware (HDK) and CANN software (Toolkit, Kernels, and NNAL), please refer to the "CANN Software Installation Guide" and select the following installation options:
   - **Installation Method**: Install on a physical machine
   - **Operating System**: Choose according to your setup
   - **Business Scenario**: Select training, inference, and development debugging

2. To install PyTorch, refer to the component [Install PyTorch Framework](https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0005.html) and [Install torch_npu Plugin](https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0006.html).

## Usage Guide
### 1. Installation Guide
1. Contact relevant personnel to obtain the MindIE Turbo package.

2. Upload the MindIE Turbo package to any path in your installation environment (e.g., `/home/package`).

3. Navigate to the directory where the package is located:

   ```bash
   cd /home/package
   ```

4. Execute the following command to install MindIE Turbo:

   ```bash
   python setup.py install
   ```

5. Navigate to the parent directory and verify the installation:

   ```bash
   cd ../
   pip show mindie_turbo
   ```

   If the following output appears, the installation was successful:

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

### 2. Quick Usage
MindIE Turbo does not modify any usage behavior, maintaining consistency with the original framework, making it easy for users to apply and migrate projects. For example, using the vLLM framework:

1. Install vLLM and vLLM-Ascend.

   Please refer to the [vLLM-Ascend Installation Documentation](https://vllm-ascend.readthedocs.io/en/latest/installation.html) for installation instructions.

2. Depending on your needs, perform offline batch inference or online service inference.
- Offline batch inference:
   Please refer to the [vLLM Offline Inference Example Documentation](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#offline-batched-inference) for inference. Below is the simplest example (from [vllm/examples/offline_inference/basic/basic.py](https://github.com/vllm-project/vllm/blob/main/examples/offline_inference/basic/basic.py), please modify as needed):

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

- Start online inference service:
Please refer to the [vLLM Online Inference Service Example Documentation](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) to start the service. Below is a simple example with Qwen2.5-1.5B-Instruct, please modify as needed:

   ```bash
   vllm serve Qwen/Qwen2.5-1.5B-Instruct
   ```

## Performance Tuning
### 1. Server Performance Optimization
When using a server for large model inference, it is recommended to enable CPU high-performance mode and transparent huge pages to improve performance and stability.

Step 1: Install the required libraries to enable CPU high-performance mode.

```
apt-get install cpufrequtils
apt install linux-tools-common linux-tools-$(uname -r)
```

Step 2: Use the `cpupower` command to set the performance mode.

```
cpupower frequency-set -g performance
```

Step 3: Enable transparent huge pages to improve performance stability.

```
echo always > /sys/kernel/mm/transparent_hugepage/enabled
```

### 2. Performance Tuning Related Environment Variables

- VLLM_OPTIMIZATION_LEVEL
  - Sets the optimization level of the vLLM inference engine, currently unused and reserved for future use
  - Used to control the performance optimization degree of vLLM, higher values indicate more aggressive optimization
  - Value range is 0-3, default is 2:
    - 0: Disable most optimizations, used for debugging
    - 1: Basic optimization level
    - 2: Medium optimization level (recommended)
    - 3: Highest optimization level, may include experimental features

## Supported Features

## Contributing

1. Fork this repository
2. Create a new branch
3. Validate changes
4. Submit code
5. Create a Pull Request
