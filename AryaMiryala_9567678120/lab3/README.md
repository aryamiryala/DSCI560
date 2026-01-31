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


### Final Performance Comparison

| M | N | C | CUDA_Direct | CUDA_Accelerated_Python | Total_Acceleration |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 512 | 3 | 3.705 | 7.712 | 1.420 | 2.61x |
| 512 | 5 | 8.525 | 7.821 | 1.591 | 5.36x |
| 512 | 7 | 15.127 | 7.252 | 1.442 | 10.49x |
| 1024 | 3 | 15.096 | 7.193 | 3.128 | 4.83x |
| 1024 | 5 | 33.261 | 7.171 | 3.110 | 10.70x |
| 1024 | 7 | 60.717 | 7.416 | 3.079 | 19.72x |
| 2048 | 3 | 59.750 | 7.440 | 15.179 | 3.94x |
| 2048 | 5 | 130.771 | 7.162 | 17.673 | 7.40x |
| 2048 | 7 | 260.529 | 7.295 | 9.143 | 28.50x |


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