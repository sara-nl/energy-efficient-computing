#!/bin/bash

#SBATCH -p thin
#SBATCH -n 128
#SBATCH -t 00:59:00
#SBATCH --exclusive 
#SBATCH --constraint=hwperf
#SBATCH --output=job_dvfs_example_1_job.out
#SBATCH --error=job_dvfs_example_1_job.err

#SBATCH --ear=on

module load 2022
module load foss/2022a
module load AMD-uProf/4.0.341

matrix_size=10000
# 2600000 is the nominal freq
# you can choose from Freq from 1500000 to 2600000 in increments of 100000
# in a more readable way (1.5 GHz, to 2.6 GHz in increments of 0.1 GHz)
frequency=2600000

echo "Launching power profiling @ Freq=$frequency"

srun --ntasks=1 --ear-cpufreq=$frequency --ear-policy=monitoring --ear-verbose=1 AMDuProfCLI timechart --event socket,power -o AMDuProf_output_power_freq_$frequency --interval 500 ../bin/mat_mul $matrix_size $matrix_size -p
