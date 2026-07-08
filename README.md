# ppscout_ws
<img width="1049" height="679" alt="image" src="https://github.com/user-attachments/assets/665edc3e-4014-4cee-a745-1cfaef9f055b" />


ROS 2 workspace for simulating an AgileX Scout Mini mobile base with a Piper manipulator arm in Gazebo. The integration package `ppscout_ros2` combines the Scout description, Piper arm URDF, Gazebo plugins, and ros2_control arm controllers into a single robot.

**Target platform:** Ubuntu 24.04 + [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/) + Gazebo Harmonic (`ros-jazzy-ros-gz`)

## Workspace layout

```
ppscout_ws/
├── src/
│   ├── ppscout_ros2/          # Scout + Piper integration (launch, URDF, controllers)
│   ├── agx_arm_description/   # Piper mesh/URDF wrapper
│   ├── agx_arm_urdf/          # AgileX Piper arm models (upstream)
│   ├── scout_ros2/            # Scout Mini description and drivers (modified upstream)
│   └── ugv_sdk/               # AgileX UGV SDK (for real hardware)
├── build/                     # colcon build artifacts (ignored by git)
├── install/
└── log/
```

## Prerequisites

Install ROS 2 Jazzy and the simulation/control packages:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2 \
  python3-colcon-common-extensions \
  python3-rosdep
```

Initialize rosdep (once per machine):

```bash
sudo rosdep init   # skip if already done
rosdep update
```

## Clone and build

```bash
git clone https://github.com/MACRO-UFMG/ppscout_ws.git
cd ppscout_ws

source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Add the last `source` line to your shell profile if you use this workspace often.

## Run the Gazebo simulation

With the workspace sourced:

```bash
ros2 launch ppscout_ros2 gazebo.launch.py
```

This starts:

- Gazebo Harmonic with an empty world
- Scout Mini + Piper arm spawned as `scout_piper`
- ROS–Gazebo bridge (`clock`, `cmd_vel`, `odom`, `tf`, `joint_states`, `imu`, `scan`, camera pan/tilt)
- RViz with the robot model
- Arm ros2_control controllers (enabled by default)

Launch arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `enable_arm_controllers` | `true` | Spawn ros2_control arm controllers (requires `ros-jazzy-gz-ros2-control`) |
| `spawn_z` | `0.18` | Spawn height (m) for `base_footprint` |

Example — simulation without arm controllers:

```bash
ros2 launch ppscout_ros2 gazebo.launch.py enable_arm_controllers:=false
```

Visualize the URDF in RViz only (no Gazebo):

```bash
ros2 launch ppscout_ros2 display.launch.py
```

## Control the Scout base

The Scout base uses Gazebo's differential-drive plugin. Send velocity commands on `/cmd_vel`:

```bash
# Drive forward at 0.3 m/s
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3}, angular: {z: 0.0}}"

# Turn in place
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"

# Stop
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

For continuous teleoperation, use a keyboard or joystick node, for example:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Other useful base topics:

| Topic | Type | Description |
|-------|------|-------------|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity commands (input) |
| `/odom` | `nav_msgs/msg/Odometry` | Wheel odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D lidar |
| `/imu` | `sensor_msgs/msg/Imu` | IMU data |

### Pan/tilt camera (optional)

```bash
ros2 topic pub --once /pan_camera_cmd std_msgs/msg/Float64 "{data: 0.5}"
ros2 topic pub --once /tilt_camera_cmd std_msgs/msg/Float64 "{data: -0.3}"
```

## Control the Piper arm

Arm motion in Gazebo is handled by **ros2_control** via `gz_ros2_control`. The default active controller is `arm_joint_trajectory_controller`.

### Verify controllers

In a second terminal (with the simulation running):

```bash
source /opt/ros/jazzy/setup.bash
source ~/ppscout_ws/install/setup.bash
ros2 control list_controllers
```

Expected output:

- `joint_state_broadcaster` — **active**
- `arm_joint_trajectory_controller` — **active**

If the arm does not move, confirm `arm_joint_trajectory_controller` is active and watch Gazebo (not just RViz).

### Move with a joint trajectory (recommended)

Send a trajectory to all six arm joints:

```bash
ros2 topic pub --once /arm_joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'],
  points: [{
    positions: [0.5, 1.0, -1.0, 0.0, 0.5, 0.0],
    time_from_start: {sec: 3, nanosec: 0}
  }]
}"
```

Or use the action interface:

```bash
ros2 action send_goal /arm_joint_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory "{
  trajectory: {
    joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'],
    points: [{
      positions: [0.5, 1.0, -1.0, 0.0, 0.5, 0.0],
      time_from_start: {sec: 3, nanosec: 0}
    }]
  }
}"
```

Return to home:

```bash
ros2 topic pub --once /arm_joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory "{
  joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'],
  points: [{
    positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    time_from_start: {sec: 3, nanosec: 0}
  }]
}"
```

### Joint limits (radians)

| Joint  | Lower | Upper |
|--------|-------|-------|
| joint1 | -2.62 |  2.62 |
| joint2 |  0.00 |  3.14 |
| joint3 | -2.97 |  0.00 |
| joint4 | -1.75 |  1.75 |
| joint5 | -1.22 |  1.22 |
| joint6 | -2.09 |  2.09 |

### Direct position commands (alternative)

Switch to the position controller:

```bash
ros2 control switch_controllers \
  --deactivate arm_joint_trajectory_controller \
  --activate arm_position_controller

ros2 topic pub --once /arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.5, 1.0, -1.0, 0.0, 0.5, 0.0]}"
```

### Gripper

```bash
ros2 control switch_controllers \
  --deactivate arm_joint_trajectory_controller \
  --activate gripper_position_controller

# 0.0 = open, 0.1 = closed (meters)
ros2 topic pub --once /gripper_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.05]}"
```

Switch back to trajectory control when done:

```bash
ros2 control switch_controllers \
  --deactivate gripper_position_controller \
  --activate arm_joint_trajectory_controller
```

## Troubleshooting

**Arm controllers fail to load or Gazebo crashes when spawning `arm_joint_trajectory_controller`**

Upgrade the joint trajectory controller package (known segfault in older Jazzy builds):

```bash
sudo apt install ros-jazzy-joint-trajectory-controller
```

**Robot falls through the ground**

Adjust spawn height:

```bash
ros2 launch ppscout_ros2 gazebo.launch.py spawn_z:=0.20
```

**Missing dependencies after pulling updates**

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

## Third-party components

This monorepo includes modified and unmodified packages from AgileX Robotics:

- [scout_ros2](https://github.com/agilexrobotics/scout_ros2) — Scout Mini description
- [agx_arm_urdf](https://github.com/agilexrobotics/agx_arm_urdf) — Piper arm URDF and meshes
- [ugv_sdk](https://github.com/agilexrobotics/ugv_sdk) — hardware SDK for the real Scout (simulation does not require it)

See each package's license file for terms. `ugv_sdk` and `scout_base` are intended for real-robot deployment; the Gazebo workflow uses `ppscout_ros2` and `scout_description` only.

## License

See individual package licenses under `src/`. The `ppscout_ros2` integration package license is pending declaration in `package.xml`.
