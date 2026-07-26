cmake_minimum_required(VERSION 3.8)
project(cortex_palnning)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclpy REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(nav2_core REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(nav2_util REQUIRED)
find_package(nav2_msgs REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install( PROGRAMS
  ${PROJECT_NAME}/dijkstra_planner.py  
  ${PROJECT_NAME}/a_star_planner.py
  ${PROJECT_NAME}/dijkstra_planner_costmap.py  
  ${PROJECT_NAME}/a_star_planner_costmap.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()