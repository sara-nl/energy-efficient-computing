#!/usr/bin/env python
import time

from collections import OrderedDict

import numpy as np
import kernel_tuner as kt
from kernel_tuner.observers.nvml import NVMLObserver

from common import *


# Compute the number of operations that the matrix multiply performs
def ops(m, n, k):
    return (m * n * k * 2 + 2 * m * k) / 1e9


def tune():
    # Size of the matrices
    m = n = k = 4096
    problem_size = (512, 512)
    total_flops = ops(m, n, k)

    metrics = OrderedDict()
    # Throughput
    metrics["GFLOP/s"] = lambda p: total_flops / (p["time"] / 1000.0)
    # Energy efficiency
    metrics["GFLOPS/W"] = lambda p: total_flops / p["nvml_energy"]

    # Tunable parameters
    tune_params = OrderedDict()
    # The nvml_gr_clock is the tunable parameter affecting the GPU frequency
    tune_params["nvml_gr_clock"] = [330, 510, 690, 870, 1050, 1230, 1410]

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

    # Grid size
    grid_div_x = ["MWG"]
    grid_div_y = ["NWG"]
    block_size_names = ["MDIMC", "NDIMC", "block_size_z"]

    # Search space restriction
    restrict = []
    restrict += ["KWG % KWI == 0"]
    restrict += ["MWG % (MDIMC * VWM) == 0"]
    restrict += ["NWG % (NDIMC * VWN) == 0"]
    restrict += ["MWG % (MDIMA * VWM) == 0"]
    restrict += ["NWG % (NDIMB * VWN) == 0"]
    restrict += ["KWG % ((MDIMC * NDIMC)/MDIMA) == 0"]
    restrict += ["KWG % ((MDIMC * NDIMC)/NDIMB) == 0"]
    restrict += ["not (MWG == 128 and NWG == 128 and MDIMC == 8 and NDIMC == 8)"]

    strategy = "greedy_mls"
    fevals = 100
    # If you select GFLOP/s the optimizer will improve performance
    to_optimize = "GFLOP/s"
    # If you select GFLOPS/W the optimizer will improve energy efficiency
    # to_optimize = 'GFLOPS/W'

    start = time.time()
    kt.tune_kernel(
        "Xgemm",
        "",
        problem_size,
        [],
        tune_params,
        block_size_names=block_size_names,
        simulation_mode=True,
        restrictions=restrict,
        grid_div_x=grid_div_x,
        grid_div_y=grid_div_y,
        strategy=strategy,
        strategy_options=dict(max_fevals=fevals),
        metrics=metrics,
        objective=to_optimize,
        cache="gemm/gemm_cache.json",
    )

    end = time.time()
    print()
    print(f"Tuning time: {end - start:.3} s")
    print()


if __name__ == "__main__":
    tune()
