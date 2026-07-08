import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    scout_pkg = get_package_share_directory('scout_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(scout_pkg, 'worlds', 'empty.sdf')
    robot_sdf = os.path.join(scout_pkg, 'sdf', 'model.sdf')
    robot_urdf = os.path.join(scout_pkg, 'urdf', 'model.urdf')

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

    with open(robot_urdf, 'r') as urdf_file:
        robot_description = {'robot_description': urdf_file.read()}

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
        arguments=[
            '-name', 'scout_mini',
            '-file', robot_sdf,
            '-z', '0.18',
        ],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(scout_pkg, 'params', 'bridge.yaml'),
            'expand_gz_topic_names': True,
            'use_sim_time': True,
        }],
        output='screen',
    )

    return LaunchDescription([
        set_scout_meshes,
        set_scout_models,
        set_scout_share,
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
    ])
