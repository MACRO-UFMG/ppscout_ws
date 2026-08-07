"""Bring up the Scout Mini + Piper arm in Gazebo Harmonic.

Starts Gazebo, spawns the robot, bridges ROS <-> Gazebo topics, loads the
arm ros2_control controllers and (optionally) RViz.

    ros2 launch ppscout_bringup sim.launch.py
"""

import os
from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetParameter

ROBOT_DESCRIPTION_TOPIC = '/robot_description'
# base_footprint z so wheel bottoms (~0.17 m below footprint) sit on ground
DEFAULT_SPAWN_Z = '0.18'


def generate_launch_description():
    spawn_z = LaunchConfiguration('spawn_z')
    enable_arm_controllers = LaunchConfiguration('enable_arm_controllers')
    use_rviz = LaunchConfiguration('rviz')

    bringup_pkg = get_package_share_directory('ppscout_bringup')
    description_pkg = get_package_share_directory('ppscout_description')
    scout_pkg = get_package_share_directory('scout_description')
    agx_pkg = get_package_share_directory('agx_arm_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(description_pkg, 'urdf', 'scout_piper.urdf.xacro')
    controllers_file = os.path.join(bringup_pkg, 'config', 'arm_controllers.yaml')
    robot_description_config = xacro.process_file(
        xacro_file, mappings={'controllers_file': controllers_file}
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    world_file = os.path.join(scout_pkg, 'worlds', 'empty.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    set_scout_meshes = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(scout_pkg, 'meshes'),
    )
    set_scout_models = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(scout_pkg, 'models'),
    )
    set_scout_share = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        str(Path(scout_pkg).parent.resolve()),
    )
    set_agx_meshes = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(agx_pkg, 'agx_arm_urdf', 'piper', 'meshes'),
    )
    set_agx_share = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        str(Path(agx_pkg).parent.resolve()),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[robot_description, {'use_sim_time': True}],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[{
            'name': 'scout_piper',
            'topic': ROBOT_DESCRIPTION_TOPIC,
            'z': spawn_z,
        }],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(bringup_pkg, 'config', 'bridge.yaml'),
            'expand_gz_topic_names': True,
            'use_sim_time': True,
        }],
        output='screen',
    )

    rviz = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(description_pkg, 'rviz', 'default.rviz')],
        parameters=[{'use_sim_time': True}],
    )

    # The arm trajectory controller and gripper controller claim disjoint
    # joints, so both can be active at the same time. The direct joint-group
    # controllers conflict with the trajectory controller and stay inactive.
    spawn_arm_controllers = Node(
        condition=IfCondition(enable_arm_controllers),
        package='controller_manager',
        executable='spawner',
        arguments=[
            '--controller-manager-timeout', '60',
            '--controller', 'joint_state_broadcaster',
            '--controller', 'arm_joint_trajectory_controller',
            '--controller', 'gripper_position_controller',
            '--controller', 'arm_position_controller', '--inactive',
            '--controller', 'arm_velocity_controller', '--inactive',
            '--controller', 'arm_effort_controller', '--inactive',
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'spawn_z',
            default_value=DEFAULT_SPAWN_Z,
            description='Spawn height (m) for base_footprint; wheels are ~0.17 m below',
        ),
        DeclareLaunchArgument(
            'enable_arm_controllers',
            default_value='true',
            description='Spawn ros2_control arm controllers (requires ros-jazzy-gz-ros2-control)',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Start RViz alongside the simulation',
        ),
        SetParameter(name='use_sim_time', value=True),
        set_scout_meshes,
        set_scout_models,
        set_scout_share,
        set_agx_meshes,
        set_agx_share,
        gazebo,
        robot_state_publisher,
        spawn,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn,
                on_exit=[
                    TimerAction(period=3.0, actions=[spawn_arm_controllers]),
                ],
            )
        ),
        bridge,
        RegisterEventHandler(
            OnProcessStart(
                target_action=bridge,
                on_start=[TimerAction(period=2.0, actions=[rviz])],
            )
        ),
    ])
