#!/bin/bash

#SBATCH -p thin
#SBATCH -n 128
#SBATCH -t 00:59:00
#SBATCH --exclusive 
#SBATCH --output=GROMACS_run_pair_ME.out
#SBATCH --error=GROMACS_run_pair_ME.err

#SBATCH --ear=on
#SBATCH --ear-policy=min_energy
#SBATCH --ear-verbose=1

module load 2022
module load foss/2022a
module load GROMACS/2021.6-foss-2022a

srun --ntasks=128 --cpus-per-task=1 gmx_mpi mdrun -s hEGFRDimer_benchmark.tpr