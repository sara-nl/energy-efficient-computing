include_directories(${PROJECT_SOURCE_DIR}/src/)

add_library(HELPER_LIB INTERFACE)
target_include_directories(HELPER_LIB INTERFACE {CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -fopenmp")

# compile the double precision binaries
add_executable(dgemm xgemm.c)
target_link_libraries(dgemm HELPER_LIB)
target_compile_definitions(dgemm PUBLIC USE_DOUBLE)


add_executable(daxpy axpy.c)
target_link_libraries(daxpy HELPER_LIB)
target_compile_definitions(daxpy PUBLIC USE_DOUBLE)



# compile the single precision binaries
add_executable(sgemm xgemm.c)
target_link_libraries(sgemm HELPER_LIB)

add_executable(saxpy axpy.c)
target_link_libraries(saxpy HELPER_LIB)

install(TARGETS dgemm sgemm daxpy saxpy 
    RUNTIME
    DESTINATION ${PROJECT_SOURCE_DIR}/bin
    )




