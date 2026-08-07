"""Joint-space control of the Piper arm and gripper.

Talks to the ros2_control controllers started by ppscout_bringup:

- arm_joint_trajectory_controller (FollowJointTrajectory action) — 6 arm joints
- gripper_position_controller (Float64MultiArray topic) — prismatic gripper

The same interface works on the real arm once a hardware ros2_control
backend exposes controllers with the same names.
"""

import rclpy
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

ARM_JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

# From ppscout_description/urdf/piper_description_scout.urdf (radians)
JOINT_LIMITS = {
    'joint1': (-2.62, 2.62),
    'joint2': (0.00, 3.14),
    'joint3': (-2.97, 0.00),
    'joint4': (-1.75, 1.75),
    'joint5': (-1.22, 1.22),
    'joint6': (-2.09, 2.09),
}

NAMED_POSES = {
    'home': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    'ready': [0.0, 1.0, -1.0, 0.0, 0.5, 0.0],
    'reach': [0.5, 1.2, -0.8, 0.0, 0.6, 0.0],
}

# Prismatic gripper joint range (meters)
GRIPPER_OPEN = 0.0
GRIPPER_CLOSED = 0.1

TRAJECTORY_ACTION = '/arm_joint_trajectory_controller/follow_joint_trajectory'
GRIPPER_TOPIC = '/gripper_position_controller/commands'


class ArmController(Node):
    """Send joint goals to the Piper arm and command the gripper."""

    def __init__(self, node_name: str = 'arm_controller'):
        super().__init__(node_name)
        self._traj_client = ActionClient(self, FollowJointTrajectory,
                                         TRAJECTORY_ACTION)
        self._gripper_pub = self.create_publisher(Float64MultiArray,
                                                  GRIPPER_TOPIC, 10)

    def wait_until_ready(self, timeout: float = 30.0) -> bool:
        """Wait for the trajectory controller action server to come up."""
        ok = self._traj_client.wait_for_server(timeout_sec=timeout)
        if not ok:
            self.get_logger().error(
                f'Timed out waiting for {TRAJECTORY_ACTION}. '
                'Is the simulation running with arm controllers enabled?')
        return ok

    # -------------------------------------------------------------------- arm

    def move_joints(self, positions, duration: float = 3.0,
                    wait: bool = True) -> bool:
        """Move the 6 arm joints to `positions` (radians) in `duration` s.

        Positions are clamped to the joint limits (with a warning).
        Blocking when wait=True; returns True if the goal was reached.
        """
        if len(positions) != len(ARM_JOINTS):
            raise ValueError(
                f'Expected {len(ARM_JOINTS)} joint positions, got {len(positions)}')
        clamped = []
        for name, value in zip(ARM_JOINTS, positions):
            lo, hi = JOINT_LIMITS[name]
            v = min(max(float(value), lo), hi)
            if v != float(value):
                self.get_logger().warning(
                    f'{name}: {value:.3f} outside [{lo}, {hi}], clamped to {v:.3f}')
            clamped.append(v)

        goal = FollowJointTrajectory.Goal()
        goal.trajectory = JointTrajectory()
        goal.trajectory.joint_names = list(ARM_JOINTS)
        point = JointTrajectoryPoint()
        point.positions = clamped
        point.time_from_start = Duration(seconds=duration).to_msg()
        goal.trajectory.points = [point]

        send_future = self._traj_client.send_goal_async(goal)
        if not wait:
            return True

        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error('Trajectory goal rejected')
            return False
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()
        ok = (result is not None and
              result.result.error_code == FollowJointTrajectory.Result.SUCCESSFUL)
        if not ok:
            self.get_logger().error(
                f'Trajectory failed: {result.result.error_string if result else "no result"}')
        return ok

    def move_named(self, name: str, duration: float = 3.0,
                   wait: bool = True) -> bool:
        """Move to a named pose from NAMED_POSES ('home', 'ready', ...)."""
        if name not in NAMED_POSES:
            raise ValueError(
                f'Unknown pose {name!r}. Available: {sorted(NAMED_POSES)}')
        return self.move_joints(NAMED_POSES[name], duration=duration, wait=wait)

    def home(self, duration: float = 3.0) -> bool:
        """Return the arm to the all-zeros home pose."""
        return self.move_named('home', duration=duration)

    # ---------------------------------------------------------------- gripper

    def set_gripper(self, position: float) -> None:
        """Command the gripper joint position in meters (0.0 open, 0.1 closed)."""
        position = min(max(float(position), GRIPPER_OPEN), GRIPPER_CLOSED)
        msg = Float64MultiArray()
        msg.data = [position]
        self._gripper_pub.publish(msg)

    def open_gripper(self) -> None:
        self.set_gripper(GRIPPER_OPEN)

    def close_gripper(self) -> None:
        self.set_gripper(GRIPPER_CLOSED)
