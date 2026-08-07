"""Visualize the Scout Mini + Piper URDF in RViz (no simulation).

Joint states come from joint_state_publisher_gui sliders.

    ros2 launch ppscout_bringup display.launch.py
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    description_pkg = get_package_share_directory('ppscout_description')

    xacro_file = os.path.join(description_pkg, 'urdf', 'scout_piper.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(description_pkg, 'rviz', 'default.rviz')],
        ),
    ])
