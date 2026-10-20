cmake_minimum_required(VERSION 3.24)
project(LocalizationRegression LANGUAGES CXX)
enable_testing()
add_executable(localization_test test.cpp ../../src/gui_and_draw/VSPChinese.cpp)
target_include_directories(localization_test PRIVATE ../../src/gui_and_draw)
target_compile_features(localization_test PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_test PRIVATE /utf-8)
endif()
add_test(NAME localization_display_boundaries COMMAND localization_test)
add_executable(localization_data_boundaries data_boundaries.cpp ../../src/gui_and_draw/VSPChinese.cpp)
target_include_directories(localization_data_boundaries PRIVATE ../../src/gui_and_draw)
target_compile_features(localization_data_boundaries PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_data_boundaries PRIVATE /utf-8)
endif()
add_test(NAME localization_opaque_data_boundaries COMMAND localization_data_boundaries)

# The full native package also runs localization_boundary_smoke.as.  This
# optional focused Linux test is useful before a complete OpenVSP build.
option(VSP_TEST_XML_TEXT "Build focused XML text serialization regression" OFF)
if(VSP_TEST_XML_TEXT)
  find_package(LibXml2 REQUIRED)
  add_executable(localization_xml_text xml_text_boundaries.cpp ../../src/xmlvsp/XmlUtil.cpp)
  target_include_directories(localization_xml_text PRIVATE ../../src/xmlvsp ../../src/util_api ../../src/util)
  target_link_libraries(localization_xml_text PRIVATE LibXml2::LibXml2)
  target_compile_features(localization_xml_text PRIVATE cxx_std_11)
  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_compile_options(localization_xml_text PRIVATE -ffunction-sections -fdata-sections)
    target_link_options(localization_xml_text PRIVATE -Wl,--gc-sections)
  else()
    message(FATAL_ERROR "VSP_TEST_XML_TEXT currently supports Linux; use the native AngelScript regression on other platforms")
  endif()
  add_test(NAME localization_xml_text_roundtrip COMMAND localization_xml_text)
endif()

add_executable(localization_catalog_driver catalog_driver.cpp ../../src/gui_and_draw/VSPChinese.cpp)
target_include_directories(localization_catalog_driver PRIVATE ../../src/gui_and_draw)
target_compile_features(localization_catalog_driver PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_catalog_driver PRIVATE /utf-8)
endif()
find_package(Python3 COMPONENTS Interpreter REQUIRED)
add_test(NAME localization_catalog
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../check_translation_catalog.py
          --driver $<TARGET_FILE:localization_catalog_driver>)
add_test(NAME localization_catalog_guard_tests
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_translation_catalog.py)
add_test(NAME localization_help_anchors
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_help_anchors.py)
add_test(NAME localization_help_build_layout
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_help_build_layout.py)
add_test(NAME localization_candidate_identity
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_localization_release_guard.py)

# Keep the material action distinct from custom geometry and opaque user names.
add_executable(localization_material_context material_label_context.cpp ../../src/gui_and_draw/VSPChinese.cpp)
target_include_directories(localization_material_context PRIVATE ../../src/gui_and_draw)
target_compile_features(localization_material_context PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_material_context PRIVATE /utf-8)
endif()
add_test(NAME localization_material_label_context COMMAND localization_material_context)
add_test(NAME localization_material_source_contract
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_material_label_context.py)

add_test(NAME localization_display_source_contracts
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_display_translation_boundaries.py)
# Engineering terms are reviewed in their actual UI context, not by global replacement.
add_executable(localization_engineering_terms engineering_terms.cpp ../../src/gui_and_draw/VSPChinese.cpp)
target_include_directories(localization_engineering_terms PRIVATE ../../src/gui_and_draw)
target_compile_features(localization_engineering_terms PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_engineering_terms PRIVATE /utf-8)
endif()
add_test(NAME localization_engineering_terminology COMMAND localization_engineering_terms)
add_test(NAME localization_engineering_source_context
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_engineering_term_context.py)

# Execute the real GroupLayout label paths with minimal FLTK/device doubles.
# This is not native GUI acceptance; the source contracts bind the three callers.
set(OPAQUE_LAYOUT_GENERATED "${CMAKE_CURRENT_BINARY_DIR}/opaque_layout_generated")
add_custom_command(
  OUTPUT "${OPAQUE_LAYOUT_GENERATED}/layout_label_declarations.inc"
         "${OPAQUE_LAYOUT_GENERATED}/layout_label_definitions.inc"
  COMMAND ${Python3_EXECUTABLE} -X utf8 "${CMAKE_CURRENT_SOURCE_DIR}/../test_opaque_layout_labels.py"
          --generate "${OPAQUE_LAYOUT_GENERATED}"
  DEPENDS ../test_opaque_layout_labels.py ../check_translation_catalog.py
          ../../src/gui_and_draw/GroupLayout.cpp ../../src/gui_and_draw/GroupLayout.h
          ../../src/gui_and_draw/ParasiteDragScreen.cpp ../../src/gui_and_draw/UserParmScreen.cpp
          ../../src/cmake/VSP_Version.cmake
  VERBATIM)
add_executable(localization_opaque_layout_labels opaque_layout_labels.cpp
  ../../src/gui_and_draw/VSPChinese.cpp
  "${OPAQUE_LAYOUT_GENERATED}/layout_label_declarations.inc"
  "${OPAQUE_LAYOUT_GENERATED}/layout_label_definitions.inc")
target_include_directories(localization_opaque_layout_labels PRIVATE ../../src/gui_and_draw "${OPAQUE_LAYOUT_GENERATED}")
target_compile_features(localization_opaque_layout_labels PRIVATE cxx_std_11)
if(MSVC)
  target_compile_options(localization_opaque_layout_labels PRIVATE /utf-8)
endif()
add_test(NAME localization_opaque_layout_labels COMMAND localization_opaque_layout_labels)
add_test(NAME localization_opaque_layout_source_contract
  COMMAND ${Python3_EXECUTABLE} -X utf8 ${CMAKE_CURRENT_SOURCE_DIR}/../test_opaque_layout_labels.py)
