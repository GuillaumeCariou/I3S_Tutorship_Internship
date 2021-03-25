project(Pipeline)

cmake_minimum_required(VERSION 3.5)

set(CMAKE_CXX_STANDARD 14)

find_package(MetavisionSDK COMPONENTS devtools driver core analytics REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

add_executable(Pipeline pipeline.cpp)
