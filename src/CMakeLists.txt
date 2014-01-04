cmake_minimum_required (VERSION 2.8)
project (soylentrecipes)

############################################
# find libs
find_package(ALGLIB REQUIRED)

if ( NOT SDL_FOUND )
    message ( FATAL_ERROR "SDL not found!" )
endif ( NOT SDL_FOUND )

############################################

include_directories(BEFORE ${CMAKE_SOURCE_DIR})

set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O3 -g -DNDEBUG")
set(CMAKE_CXX_FLAGS "-Wall -std=c++11 ${SDL_CFLAGS}")

file(GLOB_RECURSE Sources soylentrecipes/*.cpp)
add_executable(soylentrecipes ${Sources})

target_link_libraries(soylentrecipes 
    ${ALGLIB_LIBRARY} 
    ${LIBS} 
)

