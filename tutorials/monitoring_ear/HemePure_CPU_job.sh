#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:15:00
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --exclusive

#SBATCH --output=HemePure_CPU.%j.out
#SBATCH --error=HemePure_CPU.%j.err
#SBATCH --job-name=HemePure_CPU

module load 2023
module load foss/2023a

srun /projects/0/energy-course/HemePure/hemepure -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out hemepure_outdir
