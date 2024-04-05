#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:15:00
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --exclusive

#SBATCH --output=NPB.out
#SBATCH --error=NPB.err
#SBATCH --job-name=NPB

module load 2023
module load foss/2023a

srun /projects/0/energy-course/NPB3.4-MZ-MPI/sp-mz.C.x
