#!/bin/bash

#SBATCH -t 00:59:00
#SBATCH -p genoa
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --output=example_1.out
#SBATCH --error=example_1.err

#SBATCH --ear=on
#SBATCH --ear-policy=monitoring
#SBATCH --ear-verbose=1

module load 2023
module load foss/2023a

# Double Precision 
srun  --ntasks=1 ../bin/dgemm 5 
srun  --ntasks=1 ../bin/dgemm 500
srun  --ntasks=1 ../bin/dgemm 1000
srun  --ntasks=1 ../bin/dgemm 1500
srun  --ntasks=1 ../bin/dgemm 2000

# Single Precision 
srun  --ntasks=1 ../bin/sgemm 5 
srun  --ntasks=1 ../bin/sgemm 500
srun  --ntasks=1 ../bin/sgemm 1000
srun  --ntasks=1 ../bin/sgemm 1500
srun  --ntasks=1 ../bin/sgemm 2000



