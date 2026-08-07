# ppscout_ws

<img width="1049" height="679" alt="Scout Mini with Piper arm in Gazebo" src="https://github.com/user-attachments/assets/665edc3e-4014-4cee-a745-1cfaef9f055b" />

ROS 2 workspace for an **AgileX Scout Mini** mobile base with a **Piper**
manipulator arm — Gazebo simulation today, structured for real-hardware
bringup next.

**Target platform:** Ubuntu 24.04 + [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/) + Gazebo Harmonic (`ros-jazzy-ros-gz`)

```
src/
├── ppscout_description/   # Combined robot model (URDF/xacro, RViz config)
├── ppscout_bringup/       # Launch files + config (sim, display, real skeleton)
├── ppscout_control/       # Python control API + CLI for base and arm
└── third_party/           # Upstream AgileX packages (scout_ros2, agx_arm_urdf, ugv_sdk)
```

Full documentation lives in [docs/](docs/README.md).

## Quick start

### 1. Install dependencies (once)

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
  ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 \
  python3-colcon-common-extensions python3-rosdep

sudo rosdep init   # skip if already done
rosdep update
```

### 2. Build

```bash
git clone https://github.com/MACRO-UFMG/ppscout_ws.git
cd ppscout_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### 3. Launch the simulation

```bash
ros2 launch ppscout_bringup sim.launch.py
```

Gazebo, RViz, the ROS↔Gazebo bridge, and the arm controllers all come up.
Options: `rviz:=false`, `enable_arm_controllers:=false`, `spawn_z:=0.20`.

### 4. Drive the base

In a second terminal (with the workspace sourced):

```bash
ros2 run ppscout_control drive --linear 0.3 --duration 2    # forward 2 s
ros2 run ppscout_control drive --angular 0.5 --duration 3   # turn in place
ros2 run teleop_twist_keyboard teleop_twist_keyboard        # keyboard teleop
```

### 5. Move the arm and gripper

```bash
ros2 run ppscout_control arm_pose ready
ros2 run ppscout_control gripper close
ros2 run ppscout_control gripper open
ros2 run ppscout_control arm_pose home
```

### 6. Run the full demo

```bash
ros2 run ppscout_control demo    # arm poses + gripper + drives a 1 m square
```

## Python API

```python
import rclpy
from ppscout_control import ArmController, BaseController

rclpy.init()
base, arm = BaseController(), ArmController()

arm.wait_until_ready()
arm.move_named('ready')
base.drive(linear=0.3, duration=2.0)
arm.close_gripper()
arm.home()
```

## Documentation

| Page | Contents |
|------|----------|
| [docs/architecture.md](docs/architecture.md) | Workspace layout and how the pieces fit together |
| [docs/simulation.md](docs/simulation.md) | Launch arguments, controllers, worlds |
| [docs/base-control.md](docs/base-control.md) | Base topics, CLI, Python API |
| [docs/arm-control.md](docs/arm-control.md) | Arm controllers, joint limits, CLI, Python API |
| [docs/hardware.md](docs/hardware.md) | Real-robot bringup plan (CAN, scout_base, Piper) |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common problems and fixes |

## Third-party components

`src/third_party/` contains packages from
[AgileX Robotics](https://github.com/agilexrobotics), kept close to
upstream: [scout_ros2](https://github.com/agilexrobotics/scout_ros2)
(Scout description + real-robot driver),
[agx_arm_urdf](https://github.com/agilexrobotics/agx_arm_urdf) (Piper
models), and [ugv_sdk](https://github.com/agilexrobotics/ugv_sdk) (CAN
SDK for real hardware). See each package's license file for terms. The
`ppscout_*` packages are MIT licensed.
