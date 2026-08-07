# Arm control (Piper)

Arm motion is handled by **ros2_control** (`gz_ros2_control` in
simulation). Controllers are defined in
[arm_controllers.yaml](../src/ppscout_bringup/config/arm_controllers.yaml)
and spawned by `sim.launch.py`.

## Controllers

| Controller | Claims | Default state | Interface |
|------------|--------|---------------|-----------|
| `joint_state_broadcaster` | — | active | publishes `/joint_states` |
| `arm_joint_trajectory_controller` | joint1–joint6 | active | `FollowJointTrajectory` action / `JointTrajectory` topic |
| `gripper_position_controller` | gripper | active | `Float64MultiArray` topic |
| `arm_position_controller` | joint1–joint6 | inactive | `Float64MultiArray` topic |
| `arm_velocity_controller` | joint1–joint6 | inactive | `Float64MultiArray` topic |
| `arm_effort_controller` | joint1–joint6 | inactive | `Float64MultiArray` topic |

The trajectory controller and gripper controller claim disjoint joints, so
both stay active together — no switching needed for pick-and-place.

Check state at any time:

```bash
ros2 control list_controllers
```

## Joint limits (radians)

| Joint | Lower | Upper |
|-------|-------|-------|
| joint1 | -2.62 | 2.62 |
| joint2 | 0.00 | 3.14 |
| joint3 | -2.97 | 0.00 |
| joint4 | -1.75 | 1.75 |
| joint5 | -1.22 | 1.22 |
| joint6 | -2.09 | 2.09 |
| gripper | 0.0 (open) | 0.1 m (closed) |

## CLI

```bash
# Named poses (defined in ppscout_control/arm.py)
ros2 run ppscout_control arm_pose home
ros2 run ppscout_control arm_pose ready --time 4

# Explicit joint positions (radians, joint1..joint6)
ros2 run ppscout_control arm_pose -- 0.5 1.0 -1.0 0.0 0.5 0.0

# Gripper
ros2 run ppscout_control gripper open
ros2 run ppscout_control gripper close
ros2 run ppscout_control gripper 0.05
```

## Python API

```python
import rclpy
from ppscout_control import ArmController

rclpy.init()
arm = ArmController()
arm.wait_until_ready()

arm.move_named('ready')                          # named pose, blocks until done
arm.move_joints([0.5, 1.0, -1.0, 0, 0.5, 0],     # explicit positions (clamped
                duration=4.0)                    #  to joint limits)
arm.close_gripper()
arm.open_gripper()
arm.set_gripper(0.05)                            # meters
arm.home()
```

Named poses live in `NAMED_POSES` in
[arm.py](../src/ppscout_control/ppscout_control/arm.py) — add your own there.

## Raw interfaces (no ppscout_control)

Single-point trajectory via topic:

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

Action interface (reports result):

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

Gripper:

```bash
ros2 topic pub --once /gripper_position_controller/commands \
  std_msgs/msg/Float64MultiArray "{data: [0.05]}"
```

## Direct position/velocity/effort control (advanced)

The joint-group controllers conflict with the trajectory controller
(same joints), so switch explicitly:

```bash
ros2 control switch_controllers \
  --deactivate arm_joint_trajectory_controller \
  --activate arm_position_controller

ros2 topic pub --once /arm_position_controller/commands \
  std_msgs/msg/Float64MultiArray "{data: [0.5, 1.0, -1.0, 0.0, 0.5, 0.0]}"

# Switch back when done
ros2 control switch_controllers \
  --deactivate arm_position_controller \
  --activate arm_joint_trajectory_controller
```
