"""
===========================================
Crt Sampler implemented on GPU
===========================================

# Author: Jiawen Wu <wjw19960807@163.com>; Chaojie Wang <xd_silly@163.com>
# License: Apache License Version 2.0

check by chaojie

import pydpm.distribution as DSG
import numpy as np
import matplotlib.pyplot as plt
import time

start_time = time.time()
a = DSG.crt(10, 0.5, 100000)
end_time = time.time()
print('DSG takes {:<8.4f} second, mean: {:<8.4f}, std: {:<8.4f}'.format(end_time - start_time, np.mean(a), np.std(a)))

"""

import numpy as np
from pycuda.compiler import SourceModule
from .pre_process import para_preprocess
import pycuda.autoinit
import pydpm.distribution.compat


Sampler = SourceModule("""
#include <stdio.h>

__device__ int cudarand(long long seed)
{
    if (seed == 0)
    {
        seed = 1;
    }
    long long temp=(48271 * seed + 0) % 2147483647;
    return temp;
}

__global__ void rand_Crt(float* randomseed, int* target, int* matrix_scale, float* point, float* p)
{
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < matrix_scale[0])
    {
        int token, table;
        int current_scale=idx/matrix_scale[1];
        int seed = randomseed[idx] * 2147483647;
        float num = point[current_scale];
        float cum_sum = p[current_scale];

        if(num<0.5)
        {
            table = 0;
        }
        else
        {
            for (token = 1, table = 1; token<num; token++)
            {
                seed = cudarand(seed);
                if ((((float)seed) / 2147483647.0) <= cum_sum / (cum_sum + token))
                    table++;
            }
        }
        target[idx] = table;
    }
}

""")

def crt(point, p, times=1,device='cpu'):

    point, p, output, matrix_scale, randomseed, partition, single_number = para_preprocess(times, np.float32, np.int32, point, p)

    func = Sampler.get_function('rand_Crt')
    func(randomseed, output, matrix_scale, point, p, grid=(partition[0], 1, 1), block=(partition[1], 1, 1))

    if device == 'cpu':
        output = output.get()
    if single_number:
        return output[0]
    return output