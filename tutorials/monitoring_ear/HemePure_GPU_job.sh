#!/bin/bash

#SBATCH -p gpu
#SBATCH --gpus-per-node=1 
#SBATCH -t 00:15:00
#SBATCH --exclusive

#SBATCH --output=HemePure_GPU.%j.out
#SBATCH --error=HemePure_GPU.%j.err
#SBATCH --job-name=HemePure_GPU

module load 2023
module load foss/2023a
module load CUDA/12.1.1


OUTPUT_DIR=hemepure_gpu_outdir
rm -rf $OUTPUT_DIR # HemePure needs a fresh dir to run.

# In General it is best to use 1 MPI rank per gpu. 
# For the 1 GPU case, 2 extra mpi ranks are needed for code on the host.

srun --ntasks 3 /projects/0/energy-course/HemePure/hemepure_gpu -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out $OUTPUT_DIR