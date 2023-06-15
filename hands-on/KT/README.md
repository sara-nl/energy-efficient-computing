
# Kernel Tuner

## Installing Kernel Tuner

First we need to load the appropriate modules on Snellius.

```bash
module purge
module load 2022
module load foss/2022a
```

After the appropriate modules are loaded, we can install the Python packages that we need today.

```bash
pip install pycuda
pip install pyopencl
pip install cupy
pip install pynvml
```

While in general [Kernel Tuner](https://github.com/KernelTuner/kernel_tuner) is available via PyPI, we need a specific branch for this tutorial, so we are going to install it from GitHub.

```bash
pip install git+https://github.com/KernelTuner/kernel_tuner.git@energy_tutorial
```

We can also install the [KT Dashboard](https://github.com/KernelTuner/dashboard) to visualize the data after (or during) tuning.

```bash
pip install git+https://github.com/KernelTuner/dashboard
```

We only need to install the necessary software once.

## GEMM (cached version)

During this event we are not allowed to change the frequencies on the Snellius nodes we use, therefore we are simulating the process using the result of a previous tuning run.
To use the cached version of the GEMM kernel we need to download the compressed Kernel Tuner cache file, and move it to the proper directory.

```bash
wget -O GEMM_A100_cache.json.bz2 https://github.com/KernelTuner/kernel_tuner_tutorial/blob/master/energy/data/GEMM_NVML_NVIDIA_A100-PCIE-40GB_freq_cache.json.bz2?raw=true
bunzip2 GEMM_A100_cache.json.bz2
mv GEMM_A100_cache.json gemm/gemm_cache.json
```

You can now read the tuning script for the GEMM kernel, it is called `tuning_gemm_cached.py`.
We suggest you to first check how it works, before executing it.

```bash
python tuning_gemm_cached.py
```

After you are done, the variable `to_optimize` contains the metric that should be optimized: throughput in GFLOP/s or energy efficiency in GFLOPS/W.
If you modify the code you can see if the most performant configuration looks like the most energy efficient one.

```python
# If you select GFLOP/s the optimizer will improve performance
to_optimize = "GFLOP/s"
# If you select GFLOPS/W the optimizer will improve energy efficiency
# to_optimize = 'GFLOPS/W'
```

You can also examine the search space visually using the Dashboard.

```bash
ktdashboard gemm/gemm_cache.json
```

## Hotspot

No need to download data for the hotspot kernel, you can inspect the `tuning_hotspot.py` tuning script and try to execute it, but exploring such a large tuning space takes time.

```bash
python tuning_hotspot.py
```

You could use a different strategy than the current one (i.e. `random_sample`), lower the number of function evaluations (currently set at `1000`), or change the objective from GFLOP/s to GFLOPS/W.

```python
strategy="random_sample",
strategy_options=dict(max_fevals=1000),
objective="GFLOP/s",
```

You can also examine the search space visually using the Dashboard.

```bash
ktdashboard hotspot/hotspot_cache.json
```
