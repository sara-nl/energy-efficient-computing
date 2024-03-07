#!/bin/bash

#SBATCH -t 00:59:00
#SBATCH -p genoa
#SBATCH --nodes=1
#SBATCH --exclusive

#SBATCH --ear=on
#SBATCH --ear-policy=monitoring
#SBATCH --ear-verbose=1

module load 2023
module load foss/2023a

export OMP_NUM_THREADS=192

srun  --ntasks=1 --cpus-per-task=192 ../bin/dgemm 60 -p

srun  --ntasks=1 --cpus-per-task=192 ../bin/dgemm 600 -p 

srun  --ntasks=1 --cpus-per-task=192 ../bin/dgemm 6000 -p


