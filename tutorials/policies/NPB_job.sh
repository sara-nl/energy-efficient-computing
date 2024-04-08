#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:35:00
#SBATCH --nodes=1
#SBATCH --exclusive

#SBATCH --output=NPB.out
#SBATCH --error=NPB.err
#SBATCH --job-name=NPB

module load 2023
module load foss/2023a

# Two Class sizes available 

# | Class | Mesh size (x)  | Mesh size (y)  | Mesh size (z)  |
# |   C   |       240      |       320      |       28       |
# |   D   |      1632      |      1216      |       34       |

srun --ear=on --ear-policy=monitoring --ntasks=128 /projects/0/energy-course/NPB3.4-MZ-MPI/sp-mz.D.x
srun --ear=on --ear-policy=min_time --ntasks=128 /projects/0/energy-course/NPB3.4-MZ-MPI/sp-mz.D.x
srun --ear=on --ear-policy=min_energy --ntasks=128 /projects/0/energy-course/NPB3.4-MZ-MPI/sp-mz.D.x
