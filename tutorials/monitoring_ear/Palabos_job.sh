#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:45:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive

#SBATCH --output=Palabos.%j.out
#SBATCH --error=Palabos.%j.err
#SBATCH --job-name=Palabos

module load 2023
module load foss/2023a

# ENV variable needed to report "loops" to the EARDB
#export EARL_REPORT_LOOPS=1

# location of the binaries for the course
PROJECT_DIR=/projects/0/energy-course

# 1 node case
INPUT_FILE=input_1_node.xml

srun $PROJECT_DIR/palabos/aneurysm $PROJECT_DIR/palabos/$INPUT_FILE
