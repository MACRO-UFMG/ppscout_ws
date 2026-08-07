"""Bring up the REAL Scout Mini + Piper robot.

STATUS: skeleton — the base driver launch below is wired but UNTESTED on
hardware, and the Piper arm driver is not integrated yet.
See docs/hardware.md for the bringup plan and CAN setup.

    ros2 launch ppscout_bringup real.launch.py
"""

import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description_pkg = get_package_share_directory('ppscout_description')
    scout_base_pkg = get_package_share_directory('scout_base')

    # Same combined description as simulation; on the real robot the
    # gz_ros2_control plugin block is inert (no Gazebo running).
    xacro_file = os.path.join(description_pkg, 'urdf', 'scout_piper.urdf.xacro')
    robot_desc = xacro.process_file(xacro_file).toxml()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
    )

    # Scout Mini base driver (talks to the robot over CAN via ugv_sdk).
    # Requires the CAN interface to be up first — see docs/hardware.md.
    scout_base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(scout_base_pkg, 'launch', 'scout_mini_base.launch.py')
        ),
        launch_arguments={
            'port_name': LaunchConfiguration('can_port'),
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'can_port',
            default_value='can0',
            description='CAN interface connected to the Scout base',
        ),
        LogInfo(msg='[ppscout_bringup] real.launch.py is a skeleton: base driver '
                    'is untested on hardware and the Piper arm driver is not '
                    'integrated yet. See docs/hardware.md.'),
        robot_state_publisher,
        scout_base,
        # TODO: Piper arm hardware driver (AgileX piper_ros / CAN interface)
        # TODO: real arm ros2_control hardware interface + controller spawner
        # TODO: sensor drivers (lidar, camera, IMU)
    ])
