cmake_minimum_required (VERSION 2.8)
project (soylentrecipes)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")

############################################
# find libs
find_package(ALGLIB REQUIRED)

############################################

include_directories(BEFORE ${CMAKE_SOURCE_DIR})

set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O3 -g -DNDEBUG")
set(CMAKE_CXX_FLAGS "-Wall -std=c++11 ${SDL_CFLAGS}")

file(GLOB_RECURSE Sources soylentrecipes/*.cpp)
add_executable(soylentrecipes ${Sources})

target_link_libraries(soylentrecipes 
    ${LIBALG_LIBRARIES} 
    ${LIBS} 
)

