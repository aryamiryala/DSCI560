#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

__global__ void convolutionGPU(unsigned int *image, unsigned int *mask, unsigned int *output, int M, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row < M && col < M) {
        unsigned int res = 0;
        int offset = N / 2;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int r = row - offset + i;
                int c = col - offset + j;
                if (r >= 0 && r < M && c >= 0 && c < M)
                    res += image[r * M + c] * mask[i * N + j];
            }
        }
        output[row * M + col] = res;
    }
}

int main(int argc, char **argv) {
    int M = atoi(argv[1]);
    int N = atoi(argv[2]);
    size_t img_size = (size_t)M * M * sizeof(unsigned int);
    size_t mask_size = (size_t)N * N * sizeof(unsigned int);

    unsigned int *h_i = (unsigned int*)malloc(img_size);
    unsigned int *h_m = (unsigned int*)malloc(mask_size);
    unsigned int *h_o = (unsigned int*)malloc(img_size);
    unsigned int *d_i, *d_m, *d_o;

    cudaMalloc(&d_i, img_size); cudaMalloc(&d_m, mask_size); cudaMalloc(&d_o, img_size);
    cudaMemcpy(d_i, h_i, img_size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_m, h_m, mask_size, cudaMemcpyHostToDevice);

    dim3 threads(16, 16);
    dim3 blocks((M + 15) / 16, (M + 15) / 16);

    cudaEvent_t start, stop;
    cudaEventCreate(&start); cudaEventCreate(&stop);
    cudaEventRecord(start);
    convolutionGPU<<<blocks, threads>>>(d_i, d_m, d_o, M, N);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms = 0;
    cudaEventElapsedTime(&ms, start, stop);
    printf("%f", ms / 1000.0); // Output in seconds for consistency

    cudaFree(d_i); cudaFree(d_m); cudaFree(d_o);
    free(h_i); free(h_m); free(h_o);
    return 0;
}
