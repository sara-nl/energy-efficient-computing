#!/bin/bash

#SBATCH -p gpu
#SBATCH --gpus-per-nod=4
#SBATCH -n 72
#SBATCH -t 00:59:00
#SBATCH --exclusive 
#SBATCH --constraint=hwperf
#SBATCH --output=job_dvfs_example_2.out
#SBATCH --error=job_dvfs_example_2.err

#SBATCH --ear=on

module load 2022
module load foss/2022a
module load pmt/1.1.0-GCCcore-11.3.0

#warning largest known usage, 3500 x 3500 ... PMT throws a seg fault at values larger than this on AMD EPYC (ROME)
matrix_size=10000

#for frequency in {1500000..2600000..100000} #AMD EPYC 7H12 64-Core Processor
for frequency in {1300000..2400000..100000} #Intel(R) Xeon(R) Platinum 8360Y CPU @ 2.40GHz
do

    # specify the results to append
    RESULTS_FILE=dvfs_example_2_$frequency.txt
    TEMP_FILE=templog_$SLURM_JOBID.txt

    if [ -f "$RESULTS_FILE" ]; then
        echo "$RESULTS_FILE exists."
        echo "Removing $RESULTS_FILE"
        rm $RESULTS_FILE
    fi

    echo "Running bin/mat_mul_pmt "
    srun --ntasks=1 --ear-cpufreq=$frequency --ear-policy=monitoring --ear-verbose=1 ../bin/mat_mul_pmt -p $matrix_size $matrix_size > $TEMP_FILE

    #just some dumb commands to "log the results"
    Size=$(sed -n '/Matrix Size:/p' $TEMP_FILE | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Time=$(sed -n '/PMT Seconds:/p' $TEMP_FILE | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Watt=$(sed -n '/PMT Watts:/p' $TEMP_FILE | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Joule=$(sed -n '/PMT Joules:/p' $TEMP_FILE | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')

    echo $Size $Time $Joule $Watt >> $RESULTS_FILE

    echo "Results saved to: $RESULTS_FILE"

done