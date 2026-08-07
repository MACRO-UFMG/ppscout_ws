"""Velocity-level control of the Scout Mini base.

Works identically in simulation (Gazebo diff-drive plugin) and on the real
robot (scout_base driver): both listen on /cmd_vel and publish /odom.
"""

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class BaseController(Node):
    """Publish velocity commands to the base and track odometry."""

    def __init__(self, node_name: str = 'base_controller',
                 cmd_vel_topic: str = '/cmd_vel',
                 odom_topic: str = '/odom'):
        super().__init__(node_name)
        self._cmd_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self._odom = None
        self.create_subscription(Odometry, odom_topic, self._on_odom, 10)

    # ------------------------------------------------------------------ state

    def _on_odom(self, msg: Odometry) -> None:
        self._odom = msg

    @property
    def odom(self) -> Odometry | None:
        """Latest odometry message, or None if none received yet."""
        return self._odom

    @property
    def pose_2d(self) -> tuple[float, float, float] | None:
        """(x, y, yaw) from odometry, or None if no odometry yet."""
        if self._odom is None:
            return None
        p = self._odom.pose.pose.position
        q = self._odom.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                         1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        return (p.x, p.y, yaw)

    # --------------------------------------------------------------- commands

    def set_velocity(self, linear: float = 0.0, angular: float = 0.0) -> None:
        """Publish a single velocity command (m/s, rad/s).

        The diff-drive plugin keeps executing the last command, so call
        stop() (or drive(), which stops for you) when done.
        """
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self._cmd_pub.publish(msg)

    def stop(self) -> None:
        """Command zero velocity."""
        self.set_velocity(0.0, 0.0)

    def drive(self, linear: float = 0.0, angular: float = 0.0,
              duration: float = 1.0, rate_hz: float = 20.0) -> None:
        """Drive at a constant velocity for `duration` seconds, then stop.

        Blocking; spins this node while driving so odometry stays current.
        """
        period = 1.0 / rate_hz
        end = time.monotonic() + duration
        while time.monotonic() < end and rclpy.ok():
            self.set_velocity(linear, angular)
            rclpy.spin_once(self, timeout_sec=period)
        self.stop()

    def turn(self, angle: float, angular_speed: float = 0.5) -> None:
        """Turn in place by `angle` radians (sign gives direction).

        Timed open-loop turn; accuracy depends on the low-level controller.
        """
        speed = abs(angular_speed)
        if speed <= 0.0 or angle == 0.0:
            return
        self.drive(angular=math.copysign(speed, angle),
                   duration=abs(angle) / speed)

    def move_straight(self, distance: float, speed: float = 0.3) -> None:
        """Drive straight `distance` meters (sign gives direction), open loop."""
        v = abs(speed)
        if v <= 0.0 or distance == 0.0:
            return
        self.drive(linear=math.copysign(v, distance),
                   duration=abs(distance) / v)
