# Accelerated Computing: High-Performance Matrix Operations & Python Integration

### Project Overview
This project is an exploration into the world of **GPGPU (General-Purpose computing on Graphics Processing Units)**. The goal was to investigate the performance limits of standard CPU-based algorithms and leverage **NVIDIA's CUDA** architecture to achieve massive parallel speedups. 

Starting from a pure C baseline, I developed and benchmarked several GPU acceleration strategies, ultimately creating a portable shared library that allows high-speed CUDA kernels to be invoked directly from a **Python** environment.

### Technical Milestones
* **Architectural Analysis:** Developed a baseline triple-nested loop implementation in C to establish CPU performance metrics.
* **Parallel Kernel Design:** Engineered a naïve CUDA kernel to map matrix operations across thousands of GPU threads simultaneously.
* **Shared Memory Optimization:** Implemented **Shared Memory Tiling** to minimize global memory latency, significantly increasing memory throughput.
* **Library Engineering:** Built a shared library (`.so`) using `nvcc` with a C-style interface, enabling seamless integration with Python's `ctypes`.
* **Industry Standards:** Benchmarked hand-written kernels against **cuBLAS**, NVIDIA's premier linear algebra library, to analyze optimization gaps.

### Performance Deep Dive
The following results were benchmarked on an **NVIDIA Tesla T4 GPU**:

| Implementation | Execution Time | Speedup vs. CPU |
| :--- | :--- | :--- |
| **Vanilla C (CPU)** | 83.370 sec | 1.0x |
| **Naïve CUDA** | 7.21 ms | ~11,558x |
| **Optimized Tiled CUDA** | 7.23 ms | ~11,529x |
| **cuBLAS (NVIDIA)** | 11.54 ms | ~7,224x |


#### 2D Image Convolution Scaling (GPU Time in ms)

| Image Size (M) | Filter N=3 | Filter N=5 | Filter N=7 |
| :--- | :--- | :--- | :--- |
| **512 x 512** | 1.42 ms | 1.59 ms | 1.44 ms |
| **1024 x 1024** | 3.13 ms | 3.11 ms | 3.08 ms |
| **2048 x 2048** | 15.18 ms | 17.67 ms | 9.14 ms |

> **Note:** For the largest workload (M=2048, N=7), the Python-integrated CUDA solution achieved a **28.49x speedup** over the standalone non-accelerated C executable.



### Technology Stack
* **Low-Level:** C, CUDA C++ 
* **High-Level:** Python, NumPy 
* **Interface:** Ctypes (Shared Libraries) 
* **Tooling:** NVCC Compiler, GCC, Google Colab (Tesla T4)

### Repository Contents
* `matrix_cpu.c`: The CPU-bound baseline implementation.
* `matrix_gpu.cu`: Entry-level parallelization using CUDA.
* `matrix_tiled.cu`: Advanced implementation utilizing GPU shared memory.
* `matrix_cublas.cu`: Implementation using NVIDIA’s optimized libraries.
* `matrix_lib.cu`: The core engine for the Python-accessible shared library.
* `Lab3_DSCI560.ipynb`: Full data collection, visualization, and performance analysis.