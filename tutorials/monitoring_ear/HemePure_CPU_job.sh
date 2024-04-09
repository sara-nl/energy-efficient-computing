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

PROJECT_DIR=/projects/0/energy-course

OUTPUT_DIR=hemepure_cpu_outdir
rm -rf $OUTPUT_DIR # HemePure needs a fresh dir to run.

srun $PROJECT_DIR/HemePure/hemepure -in $PROJECT_DIR/HemePure/input_bifurcation.xml -out $OUTPUT_DIR
