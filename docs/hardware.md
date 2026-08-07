# Real-robot bringup (plan)

> **Status: skeleton.** `real.launch.py` exists and wires the Scout base
> driver, but it is **untested on hardware**, and the Piper arm driver is
> not integrated yet. This page documents the plan and what already exists.

## What is already in the workspace

| Component | Package | Role on real hardware |
|-----------|---------|-----------------------|
| `ugv_sdk` | `third_party/ugv_sdk` | AgileX CAN protocol library |
| `scout_base` | `third_party/scout_ros2/scout_base` | ROS 2 driver node: `/cmd_vel` → CAN, CAN → `/odom` |
| `scout_msgs` | `third_party/scout_ros2/scout_msgs` | Scout status/command messages |
| `real.launch.py` | `ppscout_bringup` | Skeleton bringup: robot_state_publisher + scout_base |

Because `ppscout_control` talks only to `/cmd_vel`, `/odom`, and the
ros2_control controller interfaces, base control code written against the
simulation should carry over unchanged.

## Base: Scout Mini over CAN

1. Connect the Scout Mini's CAN bus via a USB-CAN adapter (e.g. candleLight/
   canable) or an onboard SocketCAN interface.
2. Bring the interface up (Scout uses 500 kbps):

   ```bash
   sudo modprobe gs_usb            # for USB-CAN adapters
   sudo ip link set can0 up type can bitrate 500000
   candump can0                    # sanity-check traffic
   ```

3. Launch:

   ```bash
   ros2 launch ppscout_bringup real.launch.py can_port:=can0
   ```

4. Drive exactly as in simulation (`/cmd_vel`, teleop,
   `ros2 run ppscout_control drive ...`).

See `third_party/scout_ros2/README.md` and `third_party/ugv_sdk/README.md`
for the upstream driver documentation.

## Arm: Piper over CAN (TODO)

The Piper arm is not wired up yet. The intended path:

1. Add AgileX's [piper_ros](https://github.com/agilexrobotics/piper_ros)
   (or `piper_sdk`) as a driver for the arm's CAN interface.
2. Expose the arm through ros2_control with a hardware interface, reusing
   the controller names from
   [arm_controllers.yaml](../src/ppscout_bringup/config/arm_controllers.yaml)
   (`arm_joint_trajectory_controller`, `gripper_position_controller`) so
   `ppscout_control` works unchanged.
3. Extend `real.launch.py`: arm driver + controller spawner (mirroring the
   spawner block in `sim.launch.py`).

Note: base and arm each have their own CAN bus/adapter — plan for `can0`
(base) and `can1` (arm).

## Remaining TODO list

- [ ] Validate `real.launch.py` base bringup on the physical Scout Mini
- [ ] Piper arm driver + ros2_control hardware interface
- [ ] Sensor drivers (lidar, camera, IMU) and matching topic names/frames
- [ ] `use_sim_time` / frame consistency check between sim and real
