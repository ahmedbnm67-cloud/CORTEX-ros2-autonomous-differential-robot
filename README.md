# CORTEX - ROS 2 Autonomous Differential Drive Robot

[![LinkedIn][linkedin-shield]][linkedin-url]
[![Project Demo][demo-shield]][demo-url]
[![ROS2][ros2-shield]][ros2-url]
[![Ubuntu][ubuntu-shield]][ubuntu-url]

<br>

<p align="center">
    <img src="images/cover.png" width="900">
</p>

---

An autonomous differential drive robot built with **ROS 2 Jazzy**, featuring robot modeling, simulation, mapping, localization, path planning, and autonomous navigation using Navigation2.

---

# Table of Contents

- About
- Features
- Packages
- Requirements
- Installation
- Usage
- Demo
- Future Work
- Contact

---
<!-- MARKDOWN LINKS -->

[linkedin-shield]: https://img.shields.io/badge/LinkedIn-Ahmed_Ashraf-blue?style=for-the-badge&logo=linkedin

[linkedin-url]: https://www.linkedin.com/in/ahmed-ashraf-778a192b1/

[demo-shield]: https://img.shields.io/badge/Project-Demo-success?style=for-the-badge&logo=linkedin

[demo-url]: https://www.linkedin.com/posts/ahmed-ashraf-778a192b1_ros2-robotics-nav2-ugcPost-7485037014556340225-o4gl/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEsUWgwBTGFyu9h41JNTlvPe18yt37L7GNY

[ros2-shield]: https://img.shields.io/badge/ROS2-Jazzy-blue?style=for-the-badge

[ros2-url]: https://docs.ros.org/en/jazzy/

[ubuntu-shield]: https://img.shields.io/badge/Ubuntu-24.04-E95420?style=for-the-badge&logo=ubuntu

[ubuntu-url]: https://ubuntu.com/
---
# About
This project demonstrates the complete software stack required for an autonomous differential drive mobile robot using ROS 2.

The robot is developed from scratch, starting with URDF modeling and simulation, then integrating ros2_control, SLAM, localization, Navigation2, and Behavior Trees to achieve autonomous navigation.

The project is intended for learning, research, and future deployment on a real robot platform.
---
# Features
- Differential Drive Mobile Robot
- URDF/Xacro Robot Description
- RViz Visualization
- Gazebo Harmonic Simulation
- ros2_control Integration
- LiDAR Simulation
- SLAM Toolbox Mapping
- AMCL Localization
- Navigation2 Stack
- Behavior Trees
---
# Packages
| Package | Description |
|---------|-------------|
| cortex_description | Robot model, URDF, meshes and simulation configuration |
| cortex_controller | Robot controllers using ros2_control |
| cortex_mapping | SLAM configuration |
| cortex_localization | AMCL localization |
| cortex_navigation | Navigation2 configuration |
| cortex_motion | Motion behaviors |
| cortex_planning | Planning modules |
| cortex_bringup | Launch files |
---
# System Architecture
cortex_ws
├── src
│   ├── cortex_description
│   ├── cortex_controller
│   ├── cortex_mapping
│   ├── cortex_localization
│   ├── cortex_navigation
│   ├── cortex_motion
│   ├── cortex_planning
│   └── cortex_bringup
---
# Requirements
- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Navigation2
- SLAM Toolbox
- RViz2
---
# Installation
mkdir cortex_ws

cd ~/cortex_ws

colcon build

source install/setup.bash
---
# Usage
---
