# - Try to find alglib 
# Once done this will define
#  FOUND_ALGLIB - System has AGL
#  ALGLIB_INCLUDE_DIRS - The alglib include directories
#  ALGLIB_LIBRARIES - The libraries needed to use alglib


set (ALGLIB_INCLUDE_DIR "/usr/include/")

set (ALGLIB_LIBDIR "/usr/lib/")
find_library(ALGLIB_LIBRARY alglib PATHS ${ALGLIB_LIBDIR} )

IF(ALGLIB_INCLUDE_DIR AND ALGLIB_LIBRARY)
    MESSAGE(STATUS "LIBALG_INCLUDE_DIR=${ALGLIB_INCLUDE_DIR}")
    MESSAGE(STATUS "LIBALG_LIBRARY=${ALGLIB_LIBRARY}")
    get_filename_component(ALGLIB_LIBDIR ${ALGLIB_LIBRARY} PATH)
ELSE()
  IF(ALGLIB_FIND_REQUIRED)
    MESSAGE(FATAL_ERROR "libalg required, please specify it's location.")
  ELSE()
    MESSAGE(STATUS      "libalg was not found.")
  ENDIF()
ENDIF()

set(LIBALG_LIBRARIES ${ALGLIB_LIBRARY})
set(LIBALG_INCLUDE_DIRS ${ALGLIB_INCLUDE_DIR})

