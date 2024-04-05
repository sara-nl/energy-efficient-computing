#!/bin/bash

#SBATCH -p gpu
#SBATCH --gpus-per-node=1 
#SBATCH -t 00:15:00
#SBATCH --exclusive

#SBATCH --output=HemePure_CPU.out
#SBATCH --error=HemePure_CPU.err
#SBATCH --job-name=HemePure_CPU

module load 2023
module load foss/2023a
module load CUDA/12.1.1

# In General it is best to use 1 MPI rank per gpu. 
# For the 1 GPU case, 2 extra mpi ranks are needed for code on the host.

srun --ntasks 3 /projects/0/energy-course/HemePure/hemepure_gpu -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out hemepure_outdir