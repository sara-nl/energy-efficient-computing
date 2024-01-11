include_directories(${PROJECT_SOURCE_DIR}/src/)

add_library(HELPER_LIB INTERFACE)
target_include_directories(HELPER_LIB INTERFACE {CMAKE_CURRENT_SOURCE_DIR})

# compile the double precision binaries
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -O3 -DUSE_DOUBLE=1")

add_executable(dgemm xgemm.c)
target_link_libraries(dgemm HELPER_LIB)

add_executable(daxpy axpy.c)
target_link_libraries(daxpy HELPER_LIB)

unset(CMAKE_C_FLAGS)
# compile the single precision binaries
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -O3 -DUSE_SINGLE=1")

add_executable(sgemm xgemm.c)
target_link_libraries(sgemm HELPER_LIB)

add_executable(saxpy axpy.c)
target_link_libraries(saxpy HELPER_LIB)

install(TARGETS dgemm sgemm daxpy saxpy 
    RUNTIME
    DESTINATION ${PROJECT_SOURCE_DIR}/bin
    )




