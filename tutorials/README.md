# Tutorial Overview

1. [Monitoring tutorial](monitoring/README.md)
2. [DVFS tutorial](dvfs/README.md)
3. [Energy Optimization tutorial](policies/README.md)


# Applications

1. [Micro Applications](#micro-applications)
2. [Scientific Applications](#scientific-applications)
   - [HemePure](#hemepure)


## Micro Applications
There are two simple "micro" applications, matrix-vector addtion (axpy) and dense matrix multiplation (xgemm). These can be compiled for CPU's, and NVIDIA GPUs. They can be found in `energy-efficient-computing/tutorials/micro_applications`

**Compile and run (CPU):**
Load the correct modules
```
module load 2023 
module load foss/2023a
module load CMake/3.26.3-GCCcore-12.3.0
```
Now build
```
mkdir build
cd build
cmake ..
make install
```
This will install both single and double precision versions of the axpy and xgemms in the `bin` directory.

In order to run the double prcision gemm (`dgemm`) you need to give it the matrix size...
```
./bin/dgemm 300
```
To use OpenMP parallel version:
```
./bin/dgemm -p 300
```

**Compile (GPU):**
Load the correct modules
```
module load 2023 
module load foss/2023a
module load CUDA/12.1.1
module load CMake/3.26.3-GCCcore-12.3.0
```
Now build
```
mkdir build
cd build
cmake -DENABLE_CUDA=1 ..
make install
```


## Scientific Applications
All of the Scientific applications in this tutorial can be found in the project space `/projects/0/energy-course/`
### HemePure
https://github.com/UCL-CCS/HemePure  
https://github.com/UCL-CCS/HemePure-GPU
> HemePure/HemeLB developed by the team of Prof Peter Coveney at University College London (UCL), is a software pipeline that simulates blood flow. HemePure is specifically designed to efficiently handle sparse topologies, supports real-time visualization and remote steering of the simulation and can handle fully resolved realistic vessels like those found in the human brain.

* The executables are located in the directory `/projects/0/energy-course/HemePure`. There you will find the `hemepure` and `hemepure_gpu` (CUDA enabled) exectubles.
**How to run a case**
We will be running through an example of pressure driven flow through a bifurcation available in the HemeLB download.

Launch a simulation
```
mpirun -n N <hemelb executable address> -in <input file *.xml address> -out <output directory address>
```

Snellius (CPU) example jobscript:
```
#!/bin/bash

#SBATCH -p rome
#SBATCH -t 00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --exclusive

module load 2023
module load foss/2023a

srun /projects/0/energy-course/HemePure/hemepure -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out hemepure_outdir
```
Snellius (GPU) example:
> In General it is best to use 1 MPI rank per gpu. For the 1 GPU case, 2 extra mpi ranks are needed for code on the host.
```
#!/bin/bash                                                                    

#SBATCH -p gpu                                                                 
#SBATCH -t 00:30:00                                                            
#SBATCH --gpus-per-node=1                                                      

module load 2023
module load foss/2023a
module load CUDA/12.1.1

srun --ntasks 3 /projects/0/energy-course/HemePure/hemepure_gpu -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out hemepure_outdir
```

#### Palabos
#### GROMACS
#### PyTorch