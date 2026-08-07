# Troubleshooting

## Arm controllers fail to load / Gazebo crashes when spawning the trajectory controller

Older Jazzy builds of the joint trajectory controller had a known segfault.
Upgrade it:

```bash
sudo apt update && sudo apt install ros-jazzy-joint-trajectory-controller
```

## The arm does not move

1. Check the controllers are up:

   ```bash
   ros2 control list_controllers
   ```

   `joint_state_broadcaster`, `arm_joint_trajectory_controller`, and
   `gripper_position_controller` should be **active**. If the list is
   empty, the simulation was probably launched with
   `enable_arm_controllers:=false`, or `ros-jazzy-gz-ros2-control` is
   missing.
2. Watch Gazebo, not just RViz — RViz only re-renders what
   `/joint_states` reports.
3. Make sure commanded positions are inside the joint limits
   (see [arm-control.md](arm-control.md)); the trajectory controller
   rejects/aborts unreachable goals.

## Robot falls through the ground or spawns badly

Adjust the spawn height:

```bash
ros2 launch ppscout_bringup sim.launch.py spawn_z:=0.20
```

## Meshes missing / white boxes in Gazebo

The launch file extends `GZ_SIM_RESOURCE_PATH` automatically. If meshes
still fail to resolve, rebuild and re-source so the installed share
directories exist:

```bash
colcon build --symlink-install && source install/setup.bash
```

## Missing dependencies after pulling updates

```bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

## `ros2 launch ppscout_ros2 ...` no longer works

The workspace was reorganized (2026-08): `ppscout_ros2` was split into
`ppscout_description`, `ppscout_bringup`, and `ppscout_control`. Use:

```bash
ros2 launch ppscout_bringup sim.launch.py       # was: ppscout_ros2 gazebo.launch.py
ros2 launch ppscout_bringup display.launch.py   # was: ppscout_ros2 display.launch.py
```

After pulling this change, do a clean rebuild once:

```bash
rm -rf build install log
colcon build --symlink-install
source install/setup.bash
```

## Stale nodes / weird DDS state

Kill leftover Gazebo or ROS processes between runs:

```bash
pkill -f 'gz sim'; ros2 daemon stop; ros2 daemon start
```
