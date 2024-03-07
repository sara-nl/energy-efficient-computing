#!/bin/bash

#SBATCH -t 00:59:00
#SBATCH -p genoa
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --output=example_2.out
#SBATCH --error=example_2.err

#SBATCH --ear=on
#SBATCH --ear-policy=monitoring
#SBATCH --ear-verbose=1

module load 2023
module load foss/2023a

# Serial
srun  --ntasks=1 ../bin/dgemm 2000

# Multithreaded
srun  --ntasks=1 --cpus-per-task=192 ../bin/dgemm 2000 -p

srun  --ntasks=1 --cpus-per-task=192 ../bin/dgemm 10000 -p

export OMP_PLACES=cores 
export OMP_PROC_BIND=close
srun  --ntasks=1 --cpus-per-task=96 ../bin/dgemm 10000 -p

export OMP_PLACES=cores 
export OMP_PROC_BIND=spread
srun  --ntasks=1 --cpus-per-task=96 ../bin/dgemm 10000 -p



