#include <stdio.h> // needed for ‘printf’ 
#include <omp.h> // needed for OpenMP 
#include <time.h> // needed for clock() and CLOCKS_PER_SEC etc
#include "helper.h" // local helper header to clean up code


#ifdef USE_DOUBLE
typedef double X_TYPE;
#elif USE_SINGLE
typedef float X_TYPE;
#endif

void simple_axpy(int n, X_TYPE a, X_TYPE * x, X_TYPE * y){

    printf("(Simple) saxpy of Array of size (%d)\n",n);

    for(int i=0; i<n; i++){
        y[i] = a * x[i] + y[i];
    }
}

void openmp_axpy(int n, X_TYPE a, X_TYPE * x, X_TYPE * y){
    int num_threads = omp_get_max_threads();

    printf("(OpenMP) saxpy of Array of size (%d)\n",n);
    printf("Using %d Threads\n", num_threads);
    #pragma omp parallel for
    for(int i=0; i<n; i++){
        y[i] = a * x[i] + y[i];
    }
}


int main( int argc, char *argv[] )  {

    int N;
    /* DUMB bools needed for the argument parsing logic */
    bool openmp = false;
    bool simple = true;
    bool sanity_check = false;
    
    /* VERY DUMB Argument Parsers */
    N = parse_arguments(argc, argv, &simple, &openmp, &sanity_check);

    X_TYPE sx[N]; /* n is an array of N integers */
    X_TYPE sy[N]; /* n is an array of N integers */

    /* Simple saxpy */
    /*==============================*/
    if (true == simple)
    {
      clock_t t; // declare clock_t (long type)
      t = clock(); // start the clock
    
      simple_axpy(N, 2.0, sx, sy);
    
      t = clock() - t; // stop the clock    
      double time_taken = ((double)t)/CLOCKS_PER_SEC; // convert to seconds (and long to double)
      printf("TIME: %f sec\n",time_taken);
    }

    /* OpenMP parallel saxpy */
    /*==============================*/
    if (true == openmp)
    {

    // omp_get_wtime needed here because clock will sum up time for all threads
    double start = omp_get_wtime();  

    openmp_axpy(N, 2.0, sx, sy);
    
    double end = omp_get_wtime(); 
    printf("TIME: %f sec\n",(end-start));

    }


}
