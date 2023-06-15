# Energy Aware Runtime (EAR) Tutorial

>EAR documentation for use on Snellius here: https://servicedesk.surf.nl/wiki/pages/viewpage.action?pageId=62226671
>
>EAR full documentation can be found here https://gitlab.bsc.es/ear_team/ear/-/wikis/home

## Section Outline

1. [Introduction](#introduction)
2. [EARL (the library)](#EARL)
3. [Tools](#tools)
4. [Excersizes](#excersizes)


<h2 id="introduction">Introduction</h2>

The Energy Aware Runtime (EAR) package provides an energy management framework for super computers. This tutorial covers the "end-user" experience with EAR.

EAR usage on Snellius can be decomposed into two "services." 

1. The EAR library (EARL): EARL is loaded (at runtime) when launching an application through the EAR Loader (EARLO) and SLURM plugin (EARPLUG). The EARL provides functionality to monitor energy (and performance) metrics of an application and additionally the ability to select the optimal CPU frequency according to the application and the node characteristics. 

2. Tools: Which include Job accounting (via the command eacct) which queries energy information of a particular job or list of jobs from the the EAR database (EAR DB) on Snellius.

![EAR_configuration](images/EAR_config.png)

### EARD: Node Manager
The node daemon is the component in charge of providing any kind of services that requires privileged capabilities. Current version is conceived as an external process executed with root privileges.
The EARD provides the following services, each one covered by one thread:

Provides privileged metrics to EARL such as the average frequency, uncore integrated memory controller counters to compute the memory bandwidth, as well as energy metrics (DC node, DRAM and package energy).
Implements a periodic power monitoring service. This service allows EAR package to control the total energy consumed in the system.
Offers a remote API used by EARplug, EARGM and EAR commands. This API accepts requests such as get the system status, change policy settings or notify new job/end job events.


<h2 id="EARL">EARL (the library)</h2>


The EAR Library is automatically loaded with MPI applications when EAR is enabled. EAR supports the utilization of both mpirun/mpiexec and srun commands.
To enable EAR in your job script when launching an MPI application you will need to include the following SBATCH options in your job script.

`srun` is the preferred job launcher when using EAR, as the EARL is a SLURM plugin! You will collect the largest amount of energy metrics when using srun
Running MPI applications with EARL is automatic for SLURM systems when using srun. All the jobs are monitored by EAR and the Library is loaded by default when EAR is enabled in the job script. To run a job with srun and EARL there is no need to load the EAR module. When using slurm commands for job submission, both Intel and OpenMPI implementations are supported. When using sbatch/srun or salloc to submit a job, Intel MPI and OpenMPI are supported.


### Example usage in a batch script

```
#SBATCH --ear=on
#SBATCH --ear-policy=monitoring
```

FULL example:
```bash
#!/bin/bash
 
#SBATCH -p thin
#SBATCH -t 00:30:00
#SBATCH --ntasks=128
 
#SBATCH --ear=on
#SBATCH --ear-policy=monitoring
#SBATCH --ear-verbose=1
 
module load 2022
module load foss/2022a
 
srun myapplication
```




<h2 id="tools">EAR Tools</h2>

EAR is available on Snellius as a module
```
module load 2022
module load ear
```
### Job accounting (eacct)
The eacct command shows accounting information stored in the EAR DB for jobs (and step) IDs. The command uses EAR’s configuration file to determine if the user running it is privileged or not, as non-privileged users can only access their information. It provides the following options. The ear module needs to be loaded to use the eacct command.

eacct example usage
The basic usage of eacct retrieves the last 20 applications (by default) of the user executing it. The default behavior shows data from each job-step, aggregating the values from each node in said job-step. If using SLURM as a job manager, a sbatch job-step is created with the data from the entire execution. A specific job may be specified with -j option:

Default: Show the last 20 jobs (maximum) executed by the user.
```
eacct
```
Query a specific job
```
eacct -J 123456789
```
Query a specific job-step
```
eacct -J 123456789.0
```
Show metrics (averaged per job.stepid) from 3 jobs
```
eacct -j 175966,175967,175968
```



### Example:

```
squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
           2884239      thin ear_sbat benjamic  R       2:19      1 tcn352
```

```
[benjamic@int4 EAR]$ eacct -j 2884239
    JOB-STEP USER       APPLICATION      POLICY NODES AVG/DEF/IMC(GHz) TIME(s)    POWER(W) GBS     CPI   ENERGY(J)    GFLOPS/W IO(MBs) MPI%  G-POW (T/U)   G-FREQ  G-UTIL(G/MEM)
2884239-sb   benjamic   ear_sbatch_GROMA MO     1     2.57/2.60/---    386.00     596.51   ---     ---   230253       ---      ---     ---   ---           ---     ---          
2884239-0    benjamic   ear_sbatch_GROMA MO     1     2.57/2.60/1.47   348.64     617.18   8.33    0.33  215175       0.2930   0.3     77.6  0.00/---      ---     --- 
```

### Application Characterization

EAR is not only a tool that will throttle CPU Freqs, but it also allows you to collect "traces" of your application, and characterize it. This is especially handy for large many node jobs, that often prove difficult to profile. In this way EAR is also a "light-weight" profiler for large applications.

The image below illustrates the usage of EAR to show the characteristics of a variety of multi-node CPU based applications side by side. This information can be obtained via the `monitoring` policy in EAR, and visualized with the `eacct` tool.

![Application_char](images/CPU_characterization_plot.png)

### EAR Policies

By understanding an application's characteristics we can try to "guess" at which Policy will be best suited for an application. 

EAR offers three energy policies plugins: min_energy, min_time and monitoring. The last one is not a power policy, is used just for application monitoring where CPU frequency is not modified (neither memory or GPU frequency).  For application analysis monitoringcan be used with specific CPU, memory and/or GPU frequencies.

The 2 optimization policies `min_time` and `min_energy` will tune the frequency for you. The energy policy is selected by setting the `--ear-policy=policy` option when submitting a SLURM job.

#### min_energy 

The goal of this policy is to minimize the energy consumed with a limit to the performance degradation. 

This limit is set in the SLURM `--ear-policy-th` option or the configuration file. The `min_energy` policy will select the optimal frequency that minimizes energy enforcing (performance degradation <= parameter). When executing with this policy, applications starts at default frequency(specified at ear.conf).
```
PerfDegr = (CurrTime - PrevTime) / (PrevTime)
```

#### min_time


The goal of this policy is to improve the execution time while guaranteeing a minimum ratio between performance benefit and frequency increment that justifies the increased energy consumption from this frequency increment. The policy uses the SLURM parameter option mentioned above as a minimum efficiency threshold.
Example: if `--ear-policy-th=0.75`, EAR will prevent scaling to upper frequencies if the ratio between performance gain and frequency gain do not improve at least `75% (PerfGain >= (FreqGain * threshold).`

```
PerfGain=(PrevTime-CurrTime)/PrevTime
FreqGain=(CurFreq-PrevFreq)/PrevFreq
```

When launched with min_time policy, applications start at a default frequency (defined at ear.conf).




![EAR_freq](images/CPU_FREQ_palabos_weakscaling_4nodes.png)



In this image we see a 2D contour map of the Energy saving vs Time savings, which shows the Energy benefit and its associated performance loss for a 4 node run of the Lattice Boltzmann Method (LBM) CFD code Palabos (https://palabos.unige.ch).
Since LBM is a memory intensive algorithm, we see that the `min_energy` policy of EAR be most effective.

![EAR_policies](images/Palabos_4node_128ppn_foss_per_policy_V2.png)


<h2 id="exercises">Exercise</h2>

### GROMACS (https://www.gromacs.org) run of the The HECBioSim Benchmarks (https://www.hecbiosim.ac.uk/access-hpc/benchmarks)
> **GROMACS** A free and open-source software suite for high-performance molecular dynamics and output analysis.
>
> **HECBioSim benchmark suite** consists of a set of simple benchmarks for a number of popular Molecular Dynamics (MD) engines, each of which is set at a different atom count. The benchmark suite currently contains benchmarks for the AMBER, GROMACS, LAMMPS and NAMD molecular dynamics packages.

In this example we will choose the "465K atom system - hEGFR Dimer of 1IVO and 1NQL" simulation (which can be found here https://github.com/victorusu/GROMACS_Benchmark_Suite/tree/1.0.0/HECBioSim/hEGFRDimer). This simulation contains a total number of atoms = 465,399 (Protein atoms = 21,749  Lipid atoms = 134,268  Water atoms = 309,087  Ions = 295). The run will take about 10 minutes to execute (using all 128 cores of an AMD ROME node). The image below shows the simulation that we will run.

![GROMACS](images/GROMACS_sim.png)
> Image Source: 
https://www.hecbiosim.ac.uk/access-hpc/benchmarks

You will need the following input file in order to run the benchmark. Download the GROMACS benchmark run, which simulates a 465K atom system.
```
curl -LJ https://github.com/victorusu/GROMACS_Benchmark_Suite/raw/1.0.0/HECBioSim/hEGFRDimer/benchmark.tpr -o hEGFRDimer_benchmark.tpr
```

See the `ear_sbatch_GROMACS.sh` jobscript to see how to submit the GROMACS benchmark, with EAR enabled.

```bash
#!/bin/bash

#SBATCH -p thin
#SBATCH -n 128
#SBATCH -t 00:20:00
#SBATCH --exclusive 
#SBATCH --output=GROMACS_run.out
#SBATCH --error=GROMACS_run.err

#SBATCH --ear=on
#SBATCH --ear-policy=monitoring

module load 2022
module load foss/2022a
module load GROMACS/2021.6-foss-2022a

srun --ntasks=128 --cpus-per-task=1 gmx_mpi mdrun -s benchmark.tpr 
```

1. What is the best policy to save energy for the GROMACS Run?
  - How much energy do you save? 
  - What is the performance degradation for using such a policy?
  - How does the size of the domain (simulation) change things? Does the "effectiveness" policy change?
    - **20K atom system** 
    ```
    curl -LJ https://github.com/victorusu/GROMACS_Benchmark_Suite/raw/1.0.0/HECBioSim/Crambin/benchmark.tpr -o Crambin_benchmark.tpr
    ```
    - **1.4M atom system** 
    ``` 
    curl -LJ https://github.com/victorusu/GROMACS_Benchmark_Suite/raw/1.0.0/HECBioSim/hEGFRDimerPair/benchmark.tpr -o hEGFRDimerPair_benchmark.tpr
    ``` 
    - **3M atom system** 
    ```
    curl -LJ https://github.com/victorusu/GROMACS_Benchmark_Suite/raw/1.0.0/HECBioSim/hEGFRDimerSmallerPL/benchmark.tpr -o hEGFRDimerSmallerPL_benchmark.tpr
    ```

