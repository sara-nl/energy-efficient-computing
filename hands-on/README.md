# Hands on Overview

## Sessions
1. [Monitoring tutorial](monitoring/README.md)
2. [DVFS tutorial](DVFS/README.md)
3. [Kernel Tuner tutorial](KT/README.md)
3. [EAR tutorial](EAR/README.md)

# Practical information
## How to connect to Snellius

>Snellius uses a white-list of ip-addresses and only from those locations you can access the system. 

If you are connecting with eduroam (from the SURF Amsterdam office) you should be able to go directly to snellius. This IP has been whitelisted. 
```
ssh username@snellius.surf.nl
```

If you are connecting from outside SURF Amsterdam you will have to have your IP whitelisted by us. Please send us your IP address to be white listed. 
You can find the blocked ip-address when logging in to Snellius using ssh -v [login]@snellius.surf.nl.

If whitelisting is not an option for you, you can always access Snellius via the "Doornode"
```
ssh user@doornode.surfsara.nl
```
The doornode is separate login server, that can be accessed from anywhere in the world: doornode.surfsara.nl (thus using `ssh user@doornode.surfsara.nl`). This server can be accessed with your usual login and password, after which you get a menu with systems that you can login to. Select 'Snellius' and type your password a second time. You are now logged on to Snellius. Please note that you cannot copy files or use X11 when using the door node.


## How to interact with the course.

This course is a "command line" course. We assume that you are somewhat comfortable with using the command line. This comes with some caveats, mainly its not so "nice" to view images or GUIs. Though not essential to have nice "viewing" capabilities, for this course we will be looking at some nice plots `.pngs`. Here are some suggested remedies.

1. Window forwarding `ssh -X username@snellius.surf.nl`. To redirect any graphics output from the HPC system to your own system, you'll need an X-server like [XQuartz](https://www.xquartz.org). Download and install it. Then, login to the HPC system using (note that X is capitalized). 
   - To view a png while on snellius use `display file.png`
2. [MobaXterm](https://mobaxterm.mobatek.net) (windows) 
3. Visual Studio Code we have documentation on how to set it up [here](https://servicedesk.surf.nl/wiki/display/WIKI/Visual+Studio+Code+for+remote+development) (go to the Running the VS Code Server on a login node section)


## Reservations available for the course

### Day 1 (energy_efficiency_course_cpu)

How to get there
```
salloc --ntasks=32 -t 02:00:00 -p thin --reservation=energy_efficiency_course_cpu --constraint=hwperf
```


### Day 2 (energy_efficiency_course_cpu and energy_efficiency_course_gpu)

```
salloc --ntasks=32 -t 02:00:00 -p thin --reservation=energy_efficiency_course_cpu --constraint=hwperf
```
AND
```
salloc --ntasks=32 -t 02:00:00 -p thin --reservation=energy_efficiency_course_gpu --constraint=hwperf
```

---
# Examples/sources/scripts used in the course
## Sources are located in the `src/`
1. Simple saxpy (single precision a*x + b) (`saxpy.c`)
2. Simple matrix multiplication (`mat_mul.cpp`, `mat_mul.py`)
      - matrix multiplication with use of the PMT library mat_mul_pmt.cpp

### How to build all of the sources

```
sh install_examples.sh
```

### How to build each of the sources

#### 1. Simple saxpy (saxpy.py)
How to compile compile the program:
```
module purge
module load 2022
module load foss/2022a

gcc -fopenmp src/saxpy.c -o bin/saxpy
```
Note: `-fopenmp` needed here because we use a simple OpenMP parallelization example.

How to use: 
```
saxpy (array size) [-s|-p|-h]
              Invoke simple implementation of Saxpy (Single precision A X plus Y)
        -s    Invoke simple implementation of Saxpy (Single precision A X plus Y)
        -p    Invoke parallel (OpenMP) implementation of Saxpy (Single precision A X plus Y)
        -h    Display help
```
**Naive Serial implementation**
```
./bin/saxpy 200
or
./bin/saxpy -s 200
```

**Naive OpenMP implementation**
```
./bin/saxpy -p 200
```
Suggestion: Play around with the `OMP_NUM_THREADS` for your execution
```
OMP_NUM_THREADS=2 ./bin/saxpy -p 200
```

#### 2. Simple Matrix multiplication (mat_mul.c)
How to compile compile the program:
```
module purge
module load 2022
module load foss/2022a

g++ -fopenmp src/mat_mul.cpp -o bin/mat_mul
```
Note: `-fopenmp` needed here because we use a simple OpenMP parallelization example.

How to use: 
```
mat_mul (matrix size) [-s|-p|-h]
              Invoke simple implementation of matrix multiplication
        -s    Invoke simple implementation of matrix multiplication
        -p    Invoke parallel (OpenMP) implementation of matrix multiplication
        -h    Display help
```
**Naive Serial implementation**
```
./bin/mat_mul 200 200
or
./bin/mat_mul -s 200 200
```

**Naive OpenMP implementation**
```
./bin/mat_mul -p 200 200
```
Suggestion: Play around with the `OMP_NUM_THREADS` for your execution
```
OMP_NUM_THREADS=2 ./bin/mat_mul -p 200 200
```
