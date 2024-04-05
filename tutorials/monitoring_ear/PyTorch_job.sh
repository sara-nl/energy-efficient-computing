#!/bin/bash

#SBATCH -p gpu
#SBATCH --gpus-per-node=1
#SBATCH -t 00:15:00
#SBATCH --cpus-per-task=4
#SBATCH --exclusive

#SBATCH --output=PyTorch.out
#SBATCH --error=PyTorch.err
#SBATCH --job-name=PT

module load 2023
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1

# Resnet101 
python /projects/0/energy-course/PyTorch/pytorch_syntethic_benchmark.py --batch-size=32 --model=resnet101