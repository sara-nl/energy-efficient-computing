include_directories(${PROJECT_SOURCE_DIR}/src/)

add_library(HELPER_LIB INTERFACE)
target_include_directories(HELPER_LIB INTERFACE {CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp -O3 -DUSE_DOUBLE=1")
add_executable(dgemm mat_mul.c)
target_link_libraries(dgemm HELPER_LIB)
unset(CMAKE_C_FLAGS)