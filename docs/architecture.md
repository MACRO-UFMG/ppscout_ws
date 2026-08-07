# Architecture

## Workspace layout

```
ppscout_ws/
├── docs/                          # This documentation
├── src/
│   ├── ppscout_description/       # Combined robot model (URDF/xacro, RViz config)
│   ├── ppscout_bringup/           # Launch files + config (sim, display, real skeleton)
│   ├── ppscout_control/           # High-level Python control API + CLI tools
│   └── third_party/               # Upstream AgileX packages (kept as-is)
│       ├── scout_ros2/            #   Scout Mini description + real-robot base driver
│       ├── agx_arm_urdf/          #   Piper arm meshes/URDF source files
│       ├── agx_arm_description/   #   ROS 2 wrapper that installs agx_arm_urdf
│       └── ugv_sdk/               #   AgileX CAN SDK (used by scout_base on real HW)
├── build/ install/ log/           # colcon artifacts (git-ignored)
```

**Package roles**

- `ppscout_description` — owns *what the robot is*: the combined
  Scout Mini + Piper xacro, Gazebo sensor/plugin definitions, and the
  ros2_control hardware description. No launch logic.
- `ppscout_bringup` — owns *how the robot starts*: launch files and
  parameter files (controller config, ROS↔Gazebo bridge map).
- `ppscout_control` — owns *how you command it*: a small Python API
  (`BaseController`, `ArmController`) and CLI tools built on the same
  topics/actions the real robot will expose.
- `third_party/*` — upstream code; avoid editing so it stays easy to update.

## How the model is assembled

The top-level xacro [scout_piper.urdf.xacro](../src/ppscout_description/urdf/scout_piper.urdf.xacro) composes:

1. `scout_description/urdf/model.xacro` — Scout Mini body, wheels, lidar,
   IMU, pan/tilt camera (from `third_party/scout_ros2`).
2. `piper_with_gripper_scout.xacro` → `piper_description_scout.urdf` —
   the Piper arm + gripper, mounted on `base_link` at z = 0.19 m
   (`scout_to_piper_joint`).
3. `piper_ros2_control.xacro` — the `<ros2_control>` block for the arm
   joints and the `gz_ros2_control` plugin. The controller YAML path is a
   xacro argument (`controllers_file`), defaulting to
   `ppscout_bringup/config/arm_controllers.yaml`.
4. Gazebo plugins declared inline: differential drive, joint state
   publisher, odometry publisher, pan/tilt joint position controllers,
   IMU and lidar sensors.

## Data flow in simulation

```
                       ┌──────────────────────────────┐
 /cmd_vel  ──────────► │            Gazebo            │
 /pan_camera_cmd ────► │  diff-drive │ sensors │ arm  │
 /tilt_camera_cmd ───► │             │         │      │
                       └──────┬──────┴────┬────┴──┬───┘
                              │           │       │
              ros_gz_bridge (config/bridge.yaml)  │ gz_ros2_control
                              │           │       │
        /odom /tf /joint_states /imu /scan /clock │
                              │           │       ▼
                              ▼           │  controller_manager
                     robot_state_publisher│   ├─ arm_joint_trajectory_controller
                              │           │   ├─ gripper_position_controller
                              ▼           │   └─ (position/velocity/effort, inactive)
                            RViz          │       ▲
                                          │       │ FollowJointTrajectory /
                                          │       │ Float64MultiArray
                                  ppscout_control (BaseController / ArmController)
```

- **Base**: `/cmd_vel` goes through the ROS↔Gazebo bridge to the
  diff-drive plugin; odometry and sensors come back the same way.
- **Arm**: commands go through **ros2_control** (`gz_ros2_control` plugs the
  controller manager directly into the simulated joints) — no bridge topics.

## Key interfaces

| Interface | Type | Direction | Purpose |
|-----------|------|-----------|---------|
| `/cmd_vel` | `geometry_msgs/Twist` | in | Base velocity command |
| `/odom` | `nav_msgs/Odometry` | out | Wheel odometry |
| `/scan` | `sensor_msgs/LaserScan` | out | 2D lidar |
| `/imu` | `sensor_msgs/Imu` | out | IMU |
| `/joint_states` | `sensor_msgs/JointState` | out | All joint positions |
| `/arm_joint_trajectory_controller/follow_joint_trajectory` | `control_msgs/FollowJointTrajectory` action | in | Arm motion |
| `/gripper_position_controller/commands` | `std_msgs/Float64MultiArray` | in | Gripper position |
| `/pan_camera_cmd`, `/tilt_camera_cmd` | `std_msgs/Float64` | in | Camera pan/tilt |

## Sim vs real

The interfaces above are the contract: `ppscout_control` only talks to
`/cmd_vel`, `/odom`, and the ros2_control controllers, so it should work
unchanged on the real robot once:

- the real Scout base driver (`scout_base` + `ugv_sdk`, already in
  `third_party/`) provides `/cmd_vel` → CAN and `/odom`;
- a hardware ros2_control backend (or the AgileX Piper SDK) exposes the
  same controller names for the arm.

See [hardware.md](hardware.md) for the plan and current status.
