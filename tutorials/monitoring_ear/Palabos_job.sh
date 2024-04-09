#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive

#SBATCH --output=Palabos.%j.out
#SBATCH --error=Palabos.%j.err
#SBATCH --job-name=Palabos

module load 2023
module load foss/2023a


# 1 node case
INPUT_FILE=input_1_node.xml
# 4 node case (!! You need to change #SBATCH --nodes=4 !!)
#INPUT_FILE=input_4_node.xml

srun /projects/0/energy-course/palabos/aneurysm /projects/0/energy-course/palabos/$INPUT_FILE
