cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(lsSeg)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/lsseg_slicer_extension")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "William A. Romero R. (CREATIS)")
set(EXTENSION_DESCRIPTION "LS segmentation methods.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/lsseg_slicer_extension.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/lsseg_slicer_extension/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(lsseg_slicer_extension)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
