# Simulation

Target stack: **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic** (`ros-jazzy-ros-gz`).

## Launch

With the workspace built and sourced:

```bash
ros2 launch ppscout_bringup sim.launch.py
```

This starts:

- Gazebo Harmonic with an empty world
- The Scout Mini + Piper robot spawned as `scout_piper`
- `ros_gz_bridge` (clock, cmd_vel, odom, tf, joint_states, imu, scan, camera pan/tilt)
- ros2_control arm + gripper controllers
- RViz with the robot model

### Launch arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `spawn_z` | `0.18` | Spawn height (m) for `base_footprint`; wheels are ~0.17 m below |
| `enable_arm_controllers` | `true` | Spawn the ros2_control controllers (requires `ros-jazzy-gz-ros2-control`) |
| `rviz` | `true` | Start RViz alongside the simulation |

Examples:

```bash
ros2 launch ppscout_bringup sim.launch.py enable_arm_controllers:=false
ros2 launch ppscout_bringup sim.launch.py rviz:=false spawn_z:=0.20
```

## Verify it is running

```bash
ros2 topic list                 # expect /cmd_vel /odom /scan /imu /joint_states ...
ros2 control list_controllers
```

Expected controllers:

| Controller | State |
|------------|-------|
| `joint_state_broadcaster` | active |
| `arm_joint_trajectory_controller` | active |
| `gripper_position_controller` | active |
| `arm_position_controller` | inactive |
| `arm_velocity_controller` | inactive |
| `arm_effort_controller` | inactive |

## URDF-only visualization (no Gazebo)

```bash
ros2 launch ppscout_bringup display.launch.py
```

Opens RViz with a `joint_state_publisher_gui` slider window to pose the
joints by hand. Requires `ros-jazzy-joint-state-publisher-gui`.

## Changing the world

`sim.launch.py` currently loads `empty.sdf` from
`third_party/scout_ros2/scout_description/worlds/`. To use a different
world, edit `world_file` in
[sim.launch.py](../src/ppscout_bringup/launch/sim.launch.py) or add a world
to that folder.

## Regenerating a flat URDF/SDF

The model lives as xacro. If you need a plain expanded file (e.g. for an
external tool):

```bash
xacro $(ros2 pkg prefix ppscout_description)/share/ppscout_description/urdf/scout_piper.urdf.xacro > scout_piper.urdf
gz sdf -p scout_piper.urdf > scout_piper.sdf
```

## Where the pieces live

| What | Where |
|------|-------|
| Combined robot xacro | `src/ppscout_description/urdf/scout_piper.urdf.xacro` |
| Arm ros2_control block | `src/ppscout_description/urdf/piper_ros2_control.xacro` |
| Controller configuration | `src/ppscout_bringup/config/arm_controllers.yaml` |
| ROS↔Gazebo topic bridge map | `src/ppscout_bringup/config/bridge.yaml` |
| RViz config | `src/ppscout_description/rviz/default.rviz` |
