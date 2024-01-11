#include <stdio.h> // needed for ‘printf’ 
#include <stdlib.h> // needed for ‘RAND_MAX’ 
#include <omp.h> // needed for OpenMP 
#include <time.h> // needed for clock() and CLOCKS_PER_SEC etc
#include "helper.h" // local helper header to clean up code

#ifdef USE_DOUBLE
typedef double X_TYPE;
#elif USE_SINGLE
typedef float X_TYPE;
#endif



void initialize_matrices(X_TYPE** A, X_TYPE** B, X_TYPE** C, int ROWS, int COLUMNS){
    for (int i = 0 ; i < ROWS ; i++)
    {
        for (int j = 0 ; j < COLUMNS ; j++)
        {
            A[i][j] = (X_TYPE) rand() / RAND_MAX ;
            B[i][j] = (X_TYPE) rand() / RAND_MAX ;
            C[i][j] = 0.0 ;
        }
    }
}

void simple_matrix_multiply(X_TYPE** A, X_TYPE** B, X_TYPE** C, int ROWS, int COLUMNS){
    
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

void openmp_matrix_multiply(X_TYPE** A, X_TYPE** B, X_TYPE** C, int ROWS, int COLUMNS){
    
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
                C[i][j] = C[i][j] + A[i][k] * B[k][j];
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
  X_TYPE **A;
  X_TYPE **B;
  X_TYPE **C;

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

  /* Simple matrix multiplication */
  /*==============================*/
  if (true == simple)
  {
    clock_t t; // declare clock_t (long type)
    t = clock(); // start the clock
    
    simple_matrix_multiply(A, B, C, ROWS, COLUMNS);
    
    t = clock() - t; // stop the clock

    double time_taken = ((double)t)/CLOCKS_PER_SEC; // convert to seconds (and long to double)
    printf("TIME: %f sec\n",time_taken);
  }



  /* OpenMP parallel matrix multiplication */
  /*=======================================*/
  if (true == openmp)
  {
    // omp_get_wtime needed here because clock will sum up time for all threads
    double start = omp_get_wtime();  

    openmp_matrix_multiply(A, B, C, ROWS, COLUMNS);
    
    double end = omp_get_wtime(); 
    printf("TIME: %f sec\n",(end-start));
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
