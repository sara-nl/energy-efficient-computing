include_directories(${PROJECT_SOURCE_DIR}/src/)

add_library(HELPER_LIB INTERFACE)
target_include_directories(HELPER_LIB INTERFACE {CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -fopenmp -march=native")

# compile the double precision binaries
#######################################
add_executable(dgemm xgemm.c)
target_link_libraries(dgemm HELPER_LIB)
target_compile_definitions(dgemm PUBLIC USE_DOUBLE)


add_executable(daxpy axpy.c)
target_link_libraries(daxpy HELPER_LIB)
target_compile_definitions(daxpy PUBLIC USE_DOUBLE)

# compile the single precision binaries
#######################################
add_executable(sgemm xgemm.c)
target_link_libraries(sgemm HELPER_LIB)

add_executable(saxpy axpy.c)
target_link_libraries(saxpy HELPER_LIB)

install(TARGETS dgemm sgemm daxpy saxpy 
    RUNTIME
    DESTINATION ${PROJECT_SOURCE_DIR}/bin
    )


if(ENABLE_CUDA)

    enable_language(CUDA)

	find_package(CUDA REQUIRED)
	if(NOT CUDA_FOUND)
	    message(FATAL_ERROR "CUDA not found.")
	else()
	    message("CUDA found.")
	endif()

	include_directories("${CUDA_TOOLKIT_ROOT_DIR}")
	include_directories("${CUDA_TOOLKIT_ROOT_DIR}/include/")

	set(CUDA_PROPAGATE_HOST_FLAGS ON)
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -arch=sm_80") # for A100s
    if(${CMAKE_C_COMPILER_ID} STREQUAL GNU)
        message("gnu COMPILER")
        set(CMAKE_CUDA_FLAGS " -gencode arch=compute_80,code=sm_80 -lineinfo --ptxas-options=-v --disable-warnings")
    
    endif()
    message('CUDA Flags = ' ${CMAKE_CUDA_FLAGS})

    # compile the double precision binaries
    #######################################
    add_executable(dgemm_gpu xgemm.cu)
    target_link_libraries(dgemm_gpu HELPER_LIB)
    target_compile_definitions(dgemm_gpu PUBLIC USE_DOUBLE)


    # add_executable(daxpy_gpu axpy.c)
    # target_link_libraries(daxpy_gpu HELPER_LIB)
    # target_compile_definitions(daxpy_gpu PUBLIC USE_DOUBLE)

    # compile the single precision binaries
    #######################################
    add_executable(sgemm_gpu xgemm.cu)
    target_link_libraries(sgemm_gpu HELPER_LIB)

    #add_executable(saxpy_gpu axpy.c)
    #target_link_libraries(saxpy_gpu HELPER_LIB)

    install(TARGETS dgemm_gpu sgemm_gpu # daxpy_gpu saxpy_gpu
        RUNTIME
        DESTINATION ${PROJECT_SOURCE_DIR}/bin
        )

endif()



