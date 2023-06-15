#!/bin/bash

#### ATTENTION!!! HERE IS WHERE YOU WANT TO CHANGE 
#### ATTENTION!!! HERE IS WHERE YOU WANT TO CHANGE 

# specify the results file to append to
RESULTS_FILE=results_serial.txt

#### ATTENTION!!! HERE IS WHERE YOU WANT TO CHANGE 
#### ATTENTION!!! HERE IS WHERE YOU WANT TO CHANGE 


# Remove the previous results file
if [ -f "$RESULTS_FILE" ]; then
    echo "$RESULTS_FILE exists."
    echo "Removing $RESULTS_FILE"
    rm $RESULTS_FILE
fi

# loop over the matrix size
# Maybe you want to change the matrix size
# {begin .. end .. stepsize}
for matrix_size in {0..2000..200}
do
    echo "Running Size $matrix_size $matrix_size"

    # SERIAL Version
    ../bin/mat_mul_pmt -s $matrix_size $matrix_size > templog.txt

    # OpenMP Version
    #OMP_NUM_THREADS=2 OMP_PROC_BIND=CLOSE ../bin/mat_mul_pmt -p $matrix_size $matrix_size > templog.txt

    # What follows here is some messy bash stuff to "grep" the results from the runs
    Size=$(sed -n '/Matrix Size:/p' templog.txt | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Time=$(sed -n '/PMT Seconds:/p' templog.txt | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Watt=$(sed -n '/PMT Watts:/p' templog.txt | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')
    Joule=$(sed -n '/PMT Joules:/p' templog.txt | grep -Eo '[+-]?[0-9]+([.][0-9]+)?')

    # Append the results to a file   
    echo $Size $Time $Joule $Watt >> $RESULTS_FILE
done

echo "Results saved to: $RESULTS_FILE"