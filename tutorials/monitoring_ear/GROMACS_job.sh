#!/bin/bash

#SBATCH -p rome
#SBATCH -n 128
#SBATCH -t 00:59:00
#SBATCH --exclusive 

#SBATCH --output=GROMACS.%j.out
#SBATCH --error=GROMACS.%j.err
#SBATCH --job-name=GROMACS


module load 2023
module load foss/2023a
module load GROMACS/2023.3-foss-2023a

# 20K atom system  --> Crambin_benchmark.tpr
# 1.4M atom system --> hEGFRDimer_benchmark.tpr
# 3M atom system   --> hEGFRDimerSmallerPL_benchmark.tpr

srun --ntasks=128 --cpus-per-task=1 gmx_mpi mdrun -s /projects/0/energy-course/GROMACS/hEGFRDimer_benchmark.tpr