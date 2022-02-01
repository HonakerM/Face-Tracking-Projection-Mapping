# general definitions
cmake_minimum_required(VERSION 2.8)
project( ITWFaceTracking )

# include opencv 
find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )

#incldue inc
include_directories( inc )


# add bin and tests directory
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory bin )
execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory bin/tests)


# Define DNN
# Introduce preprocessor variables to keep paths of asset files
set(FACE_DETECTION_CONFIGURATION
"${PROJECT_SOURCE_DIR}/assets/deploy.prototxt")

set(FACE_DETECTION_WEIGHTS"${PROJECT_SOURCE_DIR}/assets/res10_300x300_ssd_iter_140000_fp16.caffemodel")

target_compile_definitions(${PROJECT_NAME} PRIVATE 
FACE_DETECTION_CONFIGURATION="${FACE_DETECTION_CONFIGURATION}")

target_compile_definitions(${PROJECT_NAME} PRIVATE 
FACE_DETECTION_WEIGHTS="${FACE_DETECTION_WEIGHTS}")

#add debug exeutables
add_executable( bin/tests/OpenCVInc src/tests/opencv_inc.cpp )
add_executable( bin/tests/OpenCVFaceTrack src/tests/opencv_facetrack.cpp )


# Add OpenCV to exeitables
target_link_libraries(  bin/tests/OpenCVInc ${OpenCV_LIBS} )
target_link_libraries(  bin/tests/OpenCVFaceTrack ${OpenCV_LIBS} )