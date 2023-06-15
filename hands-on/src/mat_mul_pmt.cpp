#include <stdio.h> // needed for ‘printf’ 
#include <stdlib.h> // needed for ‘RAND_MAX’ 
#include <omp.h> // needed for OpenMP 
#include <time.h> // needed for clock() and CLOCKS_PER_SEC etc
#include "helper.h" // local helper header to clean up code

// THIS IS NEW!!!!!!
#include <pmt.h> // needed for PMT
#include<iostream> // needed for CPP IO ... cout, endl etc etc


void initialize_matrices(float** A, float** B, float** C, int ROWS, int COLUMNS){
    for (int i = 0 ; i < ROWS ; i++)
    {
        for (int j = 0 ; j < COLUMNS ; j++)
        {
            A[i][j] = (float) rand() / RAND_MAX ;
            B[i][j] = (float) rand() / RAND_MAX ;
            C[i][j] = 0.0 ;
        }
    }
}

void simple_matrix_multiply(float** A, float** B, float** C, int ROWS, int COLUMNS){
    
    printf("(Simple) Matix Multiplication of 2D matricies of equal sizes (%d, %d)\n",ROWS,COLUMNS);

    for(int i=0;i<ROWS;i++)
    {
        for(int j=0;j<COLUMNS;j++)
        {
            for(int k=0;k<COLUMNS;k++)
            {
                C[i][j] += A[i][k]*B[k][j];
            }
        }
    }
}

void openmp_matrix_multiply(float** A, float** B, float** C, int ROWS, int COLUMNS){
    
    int num_threads = omp_get_max_threads();
    
    printf("(OpenMP) Matix Multiplication of 2D matricies of equal sizes (%d, %d)\n",ROWS,COLUMNS);
    printf("Using %d Threads\n", num_threads);
    
    #pragma omp parallel for 
    for (int i = 0; i < ROWS; ++i) 
    {
        for (int j = 0; j < COLUMNS; ++j) 
        {
            for (int k = 0; k < COLUMNS; ++k) 
            {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}


int main( int argc, char *argv[] )  {

  int ROWS;
  int COLUMNS;
  int N;

  /* DUMB bools needed for the argument parsing logic */
  bool openmp = false;
  bool simple = true;
  bool sanity_check = false;
  
  /* VERY DUMB Argument Parsers */
  N = parse_arguments(argc, argv, &simple, &openmp, &sanity_check);
  ROWS = N;
  COLUMNS = N;
  /* declare the arrays */
  float **A;
  float **B;
  float **C;

  /* allocate the arrays */
  A = malloc(ROWS * sizeof *A);
  B = malloc(ROWS * sizeof *B);
  C = malloc(ROWS * sizeof *C);
  for (int i=0; i<ROWS; i++)
  {
    A[i] = malloc(COLUMNS * sizeof *A[i]);
    B[i] = malloc(COLUMNS * sizeof *B[i]);
    C[i] = malloc(COLUMNS * sizeof *C[i]);
  }

  /*======================================================================*/
  /*                START of Section of the code that matters!!!          */
  /*======================================================================*/

  /* initialize the arrays */
  initialize_matrices(A, B, C, ROWS, COLUMNS);

    // THIS IS NEW !!!!!!!
    auto sensor = pmt::rapl::Rapl::create();

  /* Simple matrix multiplication */
  /*==============================*/
  if (true == simple)
  {
    //Start the PMT "sensor"
    auto start = sensor->read();
    
    simple_matrix_multiply(A, B, C, ROWS, COLUMNS);

    //End the PMT "sensor"
    auto end = sensor->read();

    /// SORRY FOR THE CPP !!!!! BUT WE ARE JUST PRINTING!!!!
    std::cout<<"RESULTS-------"<<std::endl;
    std::cout<<"Matrix Size: "<<ROWS<<std::endl;
    std::cout <<"PMT Seconds: "<< pmt::PMT::seconds(start, end) << " s"<< std::endl;
    std::cout <<"PMT Joules: " << pmt::PMT::joules(start, end) << " J" << std::endl;
    std::cout <<"PMT Watts: " << pmt::PMT::watts(start, end) << " W" << std::endl;

  }


  /* OpenMP parallel matrix multiplication */
  /*=======================================*/
  if (true == openmp)
  {
    //Start the PMT "sensor"
    auto start = sensor->read();
    
    openmp_matrix_multiply(A, B, C, ROWS, COLUMNS);

    //End the PMT "sensor"
    auto end = sensor->read();

    /// SORRY FOR THE CPP !!!!! BUT WE ARE JUST PRINTING!!!!
    std::cout<<"RESULTS-------"<<std::endl;
    std::cout<<"Matrix Size: "<<ROWS<<std::endl;
    std::cout <<"PMT Seconds: "<< pmt::PMT::seconds(start, end) << " s"<< std::endl;
    std::cout <<"PMT Joules: " << pmt::PMT::joules(start, end) << " J" << std::endl;
    std::cout <<"PMT Watts: " << pmt::PMT::watts(start, end) << " W" << std::endl;
  }

  /*======================================================================*/
  /*                 END of Section of the code that matters!!!           */
  /*======================================================================*/

  /* deallocate the arrays */
  for (int i=0; i<ROWS; i++)
  {
    free(A[i]);
    free(B[i]);
    free(C[i]);
  }
  free(A);
  free(B);
  free(C);
}