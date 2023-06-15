import os
import argparse
from collections import OrderedDict
import pycuda.driver as drv
import numpy as np
import math
import kernel_tuner

drv.init()

from kernel_tuner.observers.nvml import nvml


def get_device_name(device):
    return drv.Device(device).name().replace(" ", "_")


# TODO: fix the node names and PATH for snellius
def get_fallback():
    if os.uname()[1].startswith("node0"):
        return "/cm/shared/package/utils/bin/run-nvidia-smi"
    return "nvidia-smi"


def get_metrics(total_flops):
    metrics = OrderedDict()
    metrics["GFLOP/s"] = lambda p: total_flops / (p["time"] / 1000.0)
    metrics["GFLOPS/W"] = lambda p: total_flops / p["nvml_energy"]

    return metrics


def get_pwr_limits(device, n=None):
    d = nvml(device)
    power_limits = d.pwr_constraints
    power_limit_min = power_limits[0]
    power_limit_max = power_limits[-1]
    power_limit_min *= 1e-3  # Convert to Watt
    power_limit_max *= 1e-3  # Convert to Watt
    power_limit_round = 5
    tune_params = OrderedDict()
    if n == None:
        n = int((power_limit_max - power_limit_min) / power_limit_round)

    # Rounded power limit values
    power_limits = power_limit_round * np.round(
        (np.linspace(power_limit_min, power_limit_max, n) / power_limit_round)
    )
    power_limits = list(set([int(power_limit) for power_limit in power_limits]))
    tune_params["nvml_pwr_limit"] = power_limits
    print("Using power limits:", tune_params["nvml_pwr_limit"])
    return tune_params


def get_supported_mem_clocks(device, n=None):
    d = nvml(device)
    mem_clocks = d.supported_mem_clocks

    if n and len(mem_clocks) > n:
        mem_clocks = mem_clocks[:: int(len(mem_clocks) / n)]

    tune_params = OrderedDict()
    tune_params["nvml_mem_clock"] = mem_clocks
    print("Using mem frequencies:", tune_params["nvml_mem_clock"])
    return tune_params


def get_gr_clocks(device, n=None):
    d = nvml(device)
    mem_clock = max(d.supported_mem_clocks)
    gr_clocks = d.supported_gr_clocks[mem_clock]

    if n and (len(gr_clocks) > n):
        gr_clocks = gr_clocks[:: math.ceil(len(gr_clocks) / n)]

    tune_params = OrderedDict()
    tune_params["nvml_gr_clock"] = gr_clocks[::-1]
    print("Using clock frequencies:", tune_params["nvml_gr_clock"])
    return tune_params


def get_default_parser():
    parser = argparse.ArgumentParser(description="Tune kernel")
    parser.add_argument("-d", dest="device", nargs="?", default=0, help="GPU ID to use")
    parser.add_argument(
        "-f",
        dest="overwrite",
        action="store_true",
        help="Overwrite any existing .json files",
    )
    parser.add_argument("--suffix", help="Suffix to append to output file names")
    parser.add_argument("--tune-power-limit", action="store_true")
    parser.add_argument("--power-limit-steps", nargs="?")
    parser.add_argument("--tune-gr-clock", action="store_true")
    parser.add_argument("--gr-clock-steps", nargs="?")
    return parser


def report_most_efficient(results, tune_params, metrics):
    best_config = min(results, key=lambda x: x["nvml_energy"])
    print("most efficient configuration:")
    kernel_tuner.util.print_config_output(
        tune_params, best_config, quiet=False, metrics=metrics, units=None
    )
