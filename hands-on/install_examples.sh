#!/bin/bash

if [ -d "./bin" ] 
then
    echo "Building Examples in ./bin"
else
    mkdir bin
    echo "Building Examples in ./bin"
fi

cd src 

module purge
module load 2022
module load foss/2022a

gcc -fopenmp mat_mul.c -o ../bin/mat_mul
gcc -fopenmp saxpy.c -o ../bin/saxpy

module load pmt/1.1.0-GCCcore-11.3.0

g++ -fopenmp -lpmt -fpermissive mat_mul_pmt.cpp -o ../bin/mat_mul_pmt

echo "Executables can be found in ./bin"
