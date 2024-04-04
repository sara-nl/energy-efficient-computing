# Tutorial Overview

1. [Monitoring tutorial](monitoring/README.md)
2. [DVFS tutorial](dvfs/README.md)
3. [Energy Optimization tutorial](policies/README.md)


# Applications

1. [Micro Applications](#micro-applications)
2. [Scientific Applications](#scientific-applications)
   - [HemePure](#hemepure)
   - [Palabos](#Palabos)
   - [GROMACS](#GROMACS)
   - [PyTorch](#PyTorch)


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
#SBATCH --output=hemepurejob.%j.out
#SBATCH --error=hemepurejob.%j.err
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
#SBATCH --output=hemepuregpujob.%j.out
#SBATCH --error=hemepuregpujob.%j.err                                                            
#SBATCH --gpus-per-node=1                                                      

module load 2023
module load foss/2023a
module load CUDA/12.1.1

srun --ntasks 3 /projects/0/energy-course/HemePure/hemepure_gpu -in /projects/0/energy-course/HemePure/input_bifurcation.xml -out hemepure_outdir
```

### Palabos
https://palabos.unige.ch/
> The Palabos (Parallel Lattice Boltzmann Solver) library is a framework for general-purpose computational fluid dynamics (CFD), with a kernel based on the lattice Boltzmann method. The case we use in this course is a simulation of blood flow in a inside the 3D aneurysm geometry.

#### 1 node case:

```
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --output=palabosjob.%j.out
#SBATCH --error=palabosjob.%j.err
#SBATCH --time=0:30:0
#SBATCH -p rome --exclusive

module load 2023
module load foss/2023a

srun /projects/0/energy-course/palabos/aneurysm /projects/0/energy-course/palabos/input_1_node.xml
```

#### 4 node case:

```
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=128
#SBATCH --output=palabosjob.%j.out
#SBATCH --error=palabosjob.%j.err
#SBATCH --time=0:30:0
#SBATCH -p rome --exclusive

module load 2023
module load foss/2023a

srun /projects/0/energy-course/palabos/aneurysm /projects/0/energy-course/palabos/input_4_node.xml
```



### GROMACS


### PyTorch
> The ResNet model is based on the Deep Residual Learning for Image Recognition from this paper https://arxiv.org/abs/1512.03385 
https://pytorch.org/hub/pytorch_vision_resnet/

**torchvision should be installed in your environemnt first**
Example how to install 2023
```
module load 2023
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1
pip install torchvision==0.16.2
```

```
#!/bin/bash

#SBATCH -p gpu
#SBATCH --gpus-per-node=1
#SBATCH -t 00:20:00
#SBATCH --cpus-per-task=4
#SBATCH --output=pytorchjob.%j.out
#SBATCH --error=pytorchjob.%j.err

module load 2023
module load PyTorch/2.1.2-foss-2023a-CUDA-12.1.1

# Resnet101 
python /projects/0/energy-course/PyTorch/pytorch_syntethic_benchmark.py --batch-size=32 --model=resnet101
```