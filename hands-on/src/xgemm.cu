#include <stdio.h> // needed for ‘printf’ 
#include <stdlib.h> // needed for ‘RAND_MAX’ 
#include <omp.h> // needed for OpenMP 
#include <time.h> // needed for clock() and CLOCKS_PER_SEC etc
#include "helper.h" // local helper header to clean up code

#ifdef USE_DOUBLE
typedef double X_TYPE;
#else
typedef float X_TYPE;
#endif

void initialize_matrices(X_TYPE* A, X_TYPE* B, X_TYPE* C, int ROWS, int COLUMNS){
    for (int i = 0; i < ROWS * COLUMNS; i++)
        {
            A[i] = (X_TYPE) rand() / RAND_MAX ;
            B[i] = (X_TYPE) rand() / RAND_MAX ;
            C[i] = 0.0 ;
        }
}
__global__ void simple_matrix_multiply(X_TYPE** A, X_TYPE** B, X_TYPE** C, int ROWS, int COLUMNS){
    
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


  /* declare the arrays...  better to do it as 1D arrays for CUDA */

  // First allocated them on the host (CPU)
    X_TYPE* A = (X_TYPE*)malloc((ROWS * COLUMNS) * sizeof(X_TYPE));
    X_TYPE* B = (X_TYPE*)malloc((ROWS * COLUMNS) * sizeof(X_TYPE));
    X_TYPE* C = (X_TYPE*)malloc((ROWS * COLUMNS) * sizeof(X_TYPE));

  // Then Allocate them on the GPUs
 // Allocate device memory for a
    cudaMalloc((void**)&d_a, sizeof(float) * N);

    // Transfer data from host to device memory
    cudaMemcpy(d_a, a, sizeof(float) * N, cudaMemcpyHostToDevice);
    
  /* initialize the arrays */
  initialize_matrices(A, B, C, ROWS, COLUMNS);

  /*======================================================================*/
  /*                START of Section of the code that matters!!!          */
  /*======================================================================*/



  /* Simple matrix multiplication */
  /*==============================*/
  if (true == simple)
  {
    clock_t t; // declare clock_t (long type)
    t = clock(); // start the clock

   // Transfer data from host to device memory
    cudaMemcpy(d_a, a, sizeof(float) * N, cudaMemcpyHostToDevice);
    
    simple_matrix_multiply<<<1,1>>>(A, B, C, ROWS, COLUMNS);
    
    t = clock() - t; // stop the clock

    double time_taken = ((double)t)/CLOCKS_PER_SEC; // convert to seconds (and long to double)
    printf("TIME: %f sec\n",time_taken);
  }



  /* OpenMP parallel matrix multiplication */
  /*=======================================*/
  if (true == openmp)
  {

    printf("This OpenMP option is not implemented in this code!!!!");
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
