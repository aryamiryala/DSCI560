
#include <cuda_runtime.h>
#include <stdio.h>

__global__ void convolutionGPU(unsigned int *image, unsigned int *mask, unsigned int *output, int M, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < M && col < M) {
        unsigned int res = 0; int offset = N / 2;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int r = row - offset + i, c = col - offset + j;
                if (r >= 0 && r < M && c >= 0 && c < M)
                    res += image[r * M + c] * mask[i * N + j];
            }
        }
        output[row * M + col] = res;
    }
}

extern "C" void gpu_convolution(unsigned int *h_image, unsigned int *h_mask, unsigned int *h_output, int M, int N) {
    unsigned int *d_i, *d_m, *d_o;
    cudaMalloc(&d_i, M*M*4); cudaMalloc(&d_m, N*N*4); cudaMalloc(&d_o, M*M*4);
    cudaMemcpy(d_i, h_image, M*M*4, cudaMemcpyHostToDevice);
    cudaMemcpy(d_m, h_mask, N*N*4, cudaMemcpyHostToDevice);
    dim3 thr(16, 16); dim3 blk((M+15)/16, (M+15)/16);
    convolutionGPU<<<blk, thr>>>(d_i, d_m, d_o, M, N);
    cudaDeviceSynchronize();
    cudaMemcpy(h_output, d_o, M*M*4, cudaMemcpyDeviceToHost);
    cudaFree(d_i); cudaFree(d_m); cudaFree(d_o);
}
