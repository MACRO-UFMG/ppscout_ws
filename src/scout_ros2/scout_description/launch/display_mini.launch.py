import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('scout_description')

    default_model_path = os.path.join(pkg_share, 'urdf', 'model.urdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'scout_mini_model_display.rviz')

    gui_arg = LaunchConfiguration('gui')
    model_arg = LaunchConfiguration('model')
    rvizconfig_arg = LaunchConfiguration('rvizconfig')

    robot_description_content = ParameterValue(
        Command(['cat ', model_arg]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        condition=UnlessCondition(gui_arg),
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        parameters=[{'robot_description': robot_description_content}],
        condition=IfCondition(gui_arg),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rvizconfig_arg],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='gui', default_value='True',
            description='Flag to enable joint_state_publisher_gui'),
        DeclareLaunchArgument(
            name='model', default_value=default_model_path,
            description='Absolute path to robot model file'),
        DeclareLaunchArgument(
            name='rvizconfig', default_value=default_rviz_config_path,
            description='Absolute path to rviz config file'),
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node,
    ])
