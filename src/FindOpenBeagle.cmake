# - Try to find alglib 
# Once done this will define
#  OPENBEAGLE_INCLUDE_DIRS - The OpenBeagle include directories
#  OPENBEAGLE_LIBRARIES - The libraries needed to use OpenBeagle
#  OpenBeagle_$component_FOUND - whether given component was found
#
# Valid components: openbeagle openbeagle-Coev openbeagle-GA openbeagle-GP


SET(OPENBEAGLE_INCLUDE_DIR "/usr/include/")

IF(OPENBEAGLE_INCLUDE_DIR)
  MESSAGE(STATUS "OPENBEAGLE_INCLUDE_DIR=${OPENBEAGLE_INCLUDE_DIR}")
ELSE()
  IF(OpenBeagle_FIND_REQUIRED)
    MESSAGE(FATAL_ERROR "OpenBeagle required, please specify it's location.")
  ELSE()
    MESSAGE(STATUS      "OpenBeagle was not found.")
  ENDIF()
ENDIF()

IF( OpenBeagle_FIND_COMPONENTS )
  FOREACH(comp ${OpenBeagle_FIND_COMPONENTS})
    FIND_LIBRARY(OpenBeagle_${comp} ${comp})

    IF (OpenBeagle_${comp})
      SET(OPENBEAGLE_LIBRARIES ${OPENBEAGLE_LIBRARIES} ${OpenBeagle_${comp}})
      SET(OpenBeagle_${comp}_FOUND 1)
    ELSE()
      SET(OpenBeagle_${comp}_FOUND 0)
      IF(OpenBeagle_FIND_REQUIRED_${comp})
        MESSAGE(FATAL_ERROR "OpenBeagle ${comp} not found.")
      ELSE()
        MESSAGE(STATUS "OpenBeagle ${comp} not found.")
      ENDIF()
    ENDIF()
  ENDFOREACH()
ENDIF()

MESSAGE(STATUS "OPENBEAGLE_LIBRARIES=${OPENBEAGLE_LIBRARIES}")

set(OPENBEAGLE_INCLUDE_DIRS ${OPENBEAGLE_INCLUDE_DIR})

