#!/usr/bin/env python
import cupy as cp
from collections import OrderedDict
import numpy as np

import kernel_tuner as kt
from kernel_tuner.observers import BenchmarkObserver
from kernel_tuner.observers.nvml import NVMLObserver


def get_input_arguments(grid_rows, grid_cols):
    # maximum power density possible (say 300W for a 10mm x 10mm chip)  */
    MAX_PD = 3.0e6

    # required precision in degrees */
    PRECISION = 0.001
    SPEC_HEAT_SI = 1.75e6
    K_SI = 100

    # capacitance fitting factor    */
    FACTOR_CHIP = 0.5

    # chip parameters   */
    t_chip = 0.0005
    chip_height = 0.016
    chip_width = 0.016

    grid_height = chip_height / grid_rows
    grid_width = chip_width / grid_cols
    cap = FACTOR_CHIP * SPEC_HEAT_SI * t_chip * grid_width * grid_height
    Rx = grid_width / (2.0 * K_SI * t_chip * grid_height)
    Ry = grid_height / (2.0 * K_SI * t_chip * grid_width)
    Rz = t_chip / (K_SI * grid_height * grid_width)
    max_slope = MAX_PD / (FACTOR_CHIP * t_chip * SPEC_HEAT_SI)
    step = PRECISION / max_slope
    step_div_cap = step / cap

    return [np.float32(i) for i in [step_div_cap, 1 / Rx, 1 / Ry, 1 / Rz]]


def get_tunable_parameters(problem_size):
    tune_params = OrderedDict()

    # input sizes need at compile time
    tune_params["grid_width"] = [problem_size[0]]
    tune_params["grid_height"] = [problem_size[1]]

    # actual tunable parameters
    tune_params["block_size_x"] = [1, 2, 4, 8, 16] + [32 * i for i in range(1, 33)]
    tune_params["block_size_y"] = [2**i for i in range(6)]
    tune_params["tile_size_x"] = [i for i in range(1, 11)]
    tune_params["tile_size_y"] = [i for i in range(1, 11)]

    tune_params["temporal_tiling_factor"] = [i for i in range(1, 11)]

    max_tfactor = max(tune_params["temporal_tiling_factor"])
    tune_params["max_tfactor"] = [max_tfactor]
    tune_params["loop_unroll_factor_t"] = [i for i in range(1, max_tfactor + 1)]

    tune_params["sh_power"] = [0, 1]
    tune_params["blocks_per_sm"] = [0, 1, 2, 3, 4]

    return tune_params, max_tfactor


def get_input_data(problem_size, max_tfactor):
    input_width = problem_size[0] + 2 * max_tfactor
    input_height = problem_size[1] + 2 * max_tfactor

    # setup main input/output data with a zero border around the input
    temp_src = np.zeros((input_height, input_width), dtype=np.float32)
    temp_src[max_tfactor:-max_tfactor, max_tfactor:-max_tfactor] = (
        np.random.random(problem_size) + 324
    )
    power = np.zeros((input_height, input_width), dtype=np.float32)
    power[max_tfactor:-max_tfactor, max_tfactor:-max_tfactor] = np.random.random(
        problem_size
    )
    temp_dst = np.zeros(problem_size, dtype=np.float32)

    return temp_src, power, temp_dst


def get_device_info(device):
    """Get device info using cupy"""
    result = dict()

    cupy_info = str(cp._cupyx.get_runtime_info()).split("\n")[:-1]
    info_dict = {s.split(":")[0].strip(): s.split(":")[1].strip() for s in cupy_info}
    result["device_name"] = info_dict[f"Device {device} Name"]

    with cp.cuda.Device(0) as dev:
        result["max_threads"] = dev.attributes["MaxThreadsPerBlock"]
        result["max_shared_memory_per_block"] = dev.attributes[
            "MaxSharedMemoryPerBlock"
        ]
        result["max_shared_memory"] = dev.attributes["MaxSharedMemoryPerMultiprocessor"]

    return result


def tune(device=0):
    problem_size = (4096, 4096)

    tune_params, max_tfactor = get_tunable_parameters(problem_size)

    temp_src, power, temp_dst = get_input_data(problem_size, max_tfactor)

    dev = get_device_info(0)

    # setup arguments
    step_div_cap, Rx_1, Ry_1, Rz_1 = get_input_arguments(*problem_size)
    args = [power, temp_src, temp_dst, Rx_1, Ry_1, Rz_1, step_div_cap]

    grid_div_x = ["block_size_x", "tile_size_x"]
    grid_div_y = ["block_size_y", "tile_size_y"]
    restrictions = [
        "block_size_x*block_size_y >= 32",
        "temporal_tiling_factor % loop_unroll_factor_t == 0",
        f"block_size_x*block_size_y <= {dev['max_threads']}",
        f"(block_size_x*tile_size_x + temporal_tiling_factor * 2) * (block_size_y*tile_size_y + temporal_tiling_factor * 2) * (2+sh_power) * 4 <= {dev['max_shared_memory_per_block']}",
        f"blocks_per_sm == 0 or (((block_size_x*tile_size_x + temporal_tiling_factor * 2) * (block_size_y*tile_size_y + temporal_tiling_factor * 2) * (2+sh_power) * 4) * blocks_per_sm <= {dev['max_shared_memory']})",
    ]

    class RegisterObserver(BenchmarkObserver):
        def get_results(self):
            return {
                "num_regs": self.dev.current_module.get_function(
                    "calculate_temp"
                ).num_regs
            }

    nvmlobserver = NVMLObserver(
        ["nvml_energy", "core_freq", "mem_freq", "temperature"],
        save_all=True,
        nvidia_smi_fallback="/cm/shared/package/utils/bin/run-nvidia-smi",
    )

    metrics = OrderedDict()

    observer = [RegisterObserver(), nvmlobserver]

    # setup metric

    # Temporal tiling introduces redundant work but saves data transfers
    # needed when doing the same work in multiple kernels
    # in the GFLOP/s calculation we don't count this double work, but only the 'real' work counts
    metrics["GFLOP/s"] = lambda p: (
        (p["temporal_tiling_factor"] * 15 * problem_size[0] * problem_size[1]) / 1e9
    ) / (p["time"] / 1e3)
    metrics["GFLOPS/W"] = (
        lambda p: (
            (p["temporal_tiling_factor"] * 15 * problem_size[0] * problem_size[1]) / 1e9
        )
        / p["nvml_energy"]
    )

    metrics["reg"] = lambda p: p["num_regs"]

    # call the tuner
    results, env = kt.tune_kernel(
        "calculate_temp",
        "hotspot/hotspot.cu",
        problem_size,
        args,
        tune_params,
        metrics=metrics,
        grid_div_x=grid_div_x,
        grid_div_y=grid_div_y,
        device=device,
        cache="hotspot/hotspot_cache.json",
        restrictions=restrictions,
        verbose=True,
        observers=observer,
        lang="cupy",
        strategy="random_sample",
        strategy_options=dict(max_fevals=1000),
        objective="GFLOP/s",
    )


if __name__ == "__main__":
    device = 0
    tune(device)
