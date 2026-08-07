cmake_minimum_required(VERSION 3.8)
project(agx_arm_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../agx_arm_urdf/
  DESTINATION share/${PROJECT_NAME}/agx_arm_urdf
)

ament_package()
