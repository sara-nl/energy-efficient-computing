#!/usr/bin/env python
import sys
import time

from collections import OrderedDict
import os
import json

import numpy as np
import kernel_tuner

from kernel_tuner.observers.nvml import NVMLObserver


from common import *


unit = "GFLOP"


# Compute the number of operations that the matrix multiply performs
def ops(m, n, k):
    return (m * n * k * 2 + 2 * m * k) / 1e9


def tune(inputs, pwr_limit=None, device=0):
    path = os.path.dirname(os.path.realpath(__file__)) + "/gemm/"

    total_flops = ops(*inputs)

    m, n, k = [np.int32(i) for i in inputs]

    A = np.array(np.random.randn(m, k), order="F").astype(np.float32)
    B = np.array(np.random.randn(k, n), order="F").astype(np.float32)
    C = np.zeros((m, n), order="F").astype(np.float32)

    alpha, beta = np.random.randn(2).astype(np.float32)
    alpha, beta = np.array([1.0, 1.0]).astype(np.float32)

    kernel_string = ""
    files = [
        "common.opencl",
        "xgemm_part1.opencl",
        "xgemm_part2.opencl",
        "xgemm_part3.opencl",
    ]
    for f in files:
        with open(path + f, "r") as fp:
            kernel_string += fp.read()

    args = [m, n, k, alpha, beta, A, B, C]

    tune_params = OrderedDict()

    device_name = get_device_name(device)

    # power or freq parameters
    n_gr_clocks = 7
    n_pwr_limits = 7
    if pwr_limit:
        energy_method = "pwr"
        tune_params.update(get_pwr_limits(device, n_pwr_limits))
    else:
        energy_method = "freq"
        tune_params.update(get_gr_clocks(device, n_gr_clocks))

    tune_params["MWG"] = [16, 32, 64, 128]
    tune_params["NWG"] = [16, 32, 64, 128]
    tune_params["KWG"] = [32]
    tune_params["MDIMC"] = [8, 16, 32]
    tune_params["NDIMC"] = [8, 16, 32]
    tune_params["MDIMA"] = [8, 16, 32]
    tune_params["NDIMB"] = [8, 16, 32]
    tune_params["KWI"] = [2]
    tune_params["VWM"] = [1, 2, 4, 8]
    tune_params["VWN"] = [1, 2, 4, 8]
    tune_params["STRM"] = [0]
    tune_params["STRN"] = [0]
    tune_params["SA"] = [0, 1]
    tune_params["SB"] = [0, 1]
    tune_params["PRECISION"] = [32]

    problem_size = (m, n)

    grid_div_x = ["MWG"]
    grid_div_y = ["NWG"]
    block_size_names = ["MDIMC", "NDIMC", "block_size_z"]

    restrict = []
    restrict += ["KWG % KWI == 0"]
    restrict += ["MWG % (MDIMC * VWM) == 0"]
    restrict += ["NWG % (NDIMC * VWN) == 0"]
    restrict += ["MWG % (MDIMA * VWM) == 0"]
    restrict += ["NWG % (NDIMB * VWN) == 0"]
    restrict += ["KWG % ((MDIMC * NDIMC)/MDIMA) == 0"]
    restrict += ["KWG % ((MDIMC * NDIMC)/NDIMB) == 0"]

    restrict += ["not (MWG == 128 and NWG == 128 and MDIMC == 8 and NDIMC == 8)"]

    nvmlobserver = NVMLObserver(
        ["nvml_energy", "temperature", "core_freq", "mem_freq"],
        save_all=True,
        nvidia_smi_fallback="/cm/shared/package/utils/bin/run-nvidia-smi",
        use_locked_clocks=False,
    )

    metrics = get_metrics(total_flops)
    filename = "GEMM_NVML_" + device_name + "_" + energy_method
    print(f"{filename=}")

    start = time.time()

    results, env = kernel_tuner.tune_kernel(
        "Xgemm",
        kernel_string,
        problem_size,
        args,
        tune_params,
        block_size_names=block_size_names,
        lang="OpenCL",
        restrictions=restrict,
        verbose=False,
        compiler_options=["-I" + path],
        grid_div_x=grid_div_x,
        grid_div_y=grid_div_y,
        device=device,
        platform=0,
        iterations=72,
        observers=[nvmlobserver],
        metrics=metrics,
        cache=filename + "_cache.json",
    )

    end = time.time()
    env["execution_time"] = end - start

    with open(filename + "_output.json", "w") as fh:
        json.dump(results, fh)

    with open(filename + "_env.json", "w") as fh:
        json.dump(env, fh)

    return results, env


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pwr_limit_s = sys.argv[1]
        pwr_limit = int(pwr_limit_s)
    else:
        pwr_limit_s = None
        pwr_limit = None

    m = n = k = 4096
    device = 0

    results, env = tune([m, n, k], pwr_limit=pwr_limit, device=device)
