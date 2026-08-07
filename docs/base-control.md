# Base control (Scout Mini)

The base is driven through `/cmd_vel` (`geometry_msgs/Twist`). In
simulation this feeds Gazebo's diff-drive plugin; on the real robot the
`scout_base` driver consumes the same topic.

## Topics

| Topic | Type | Direction | Description |
|-------|------|-----------|-------------|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | in | Velocity command (`linear.x`, `angular.z`) |
| `/odom` | `nav_msgs/msg/Odometry` | out | Wheel odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | out | 2D lidar |
| `/imu` | `sensor_msgs/msg/Imu` | out | IMU |

## CLI

Timed velocity commands (stops automatically):

```bash
ros2 run ppscout_control drive --linear 0.3 --duration 2     # forward
ros2 run ppscout_control drive --angular 0.5 --duration 3    # turn in place
```

Keyboard teleop (continuous driving):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Raw topic (remember the plugin keeps executing the last command — send a
zero command to stop):

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"  # stop
```

## Python API

```python
import rclpy
from ppscout_control import BaseController

rclpy.init()
base = BaseController()

base.drive(linear=0.3, duration=2.0)      # forward for 2 s, then stop
base.move_straight(1.0, speed=0.3)        # ~1 m forward (timed, open loop)
base.turn(1.57, angular_speed=0.5)        # ~90° left (timed, open loop)
base.set_velocity(0.2, 0.0)               # continuous command...
base.stop()                               # ...until stopped
print(base.pose_2d)                       # (x, y, yaw) from /odom
```

`move_straight()` and `turn()` are open-loop timed motions — good for
demos, not precise positioning. For accurate motion, close the loop on
`/odom` (or add Nav2 later).

## Pan/tilt camera

The camera mount is commanded directly through bridged Gazebo topics:

```bash
ros2 topic pub --once /pan_camera_cmd std_msgs/msg/Float64 "{data: 0.5}"
ros2 topic pub --once /tilt_camera_cmd std_msgs/msg/Float64 "{data: -0.3}"
```
