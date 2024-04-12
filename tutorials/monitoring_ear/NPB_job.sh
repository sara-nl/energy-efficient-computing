#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:15:00
#SBATCH --nodes=1
#SBATCH --exclusive

#SBATCH --output=NPB.%j.out
#SBATCH --error=NPB.%j.err
#SBATCH --job-name=NPB

#SBATCH --reservation=ear431rome
#SBATCH --ear=on
#SBATCH --ear-policy=monitoring

module load 2023
module load foss/2023a

PROJECT_DIR=/projects/0/energy-course

# Two Class sizes available 
# | Class | Mesh size (x)  | Mesh size (y)  | Mesh size (z)  |
# |   C   |       240      |       320      |       28       |
# |   D   |      1632      |      1216      |       34       |

srun --ntasks=128 $PROJECT_DIR/NPB3.4-MZ-MPI/sp-mz.C.x

srun --ntasks=128 $PROJECT_DIR/NPB3.4-MZ-MPI/sp-mz.D.x
