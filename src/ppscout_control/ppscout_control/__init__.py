"""High-level control API for the Scout Mini base and Piper arm.

Typical usage::

    import rclpy
    from ppscout_control import ArmController, BaseController

    rclpy.init()
    base = BaseController()
    arm = ArmController()

    arm.wait_until_ready()
    arm.move_named('ready')
    base.drive(linear=0.3, duration=2.0)   # forward 2 s, then stop
    arm.close_gripper()
    arm.move_named('home')
"""

from ppscout_control.arm import (
    ARM_JOINTS,
    GRIPPER_CLOSED,
    GRIPPER_OPEN,
    JOINT_LIMITS,
    NAMED_POSES,
    ArmController,
)
from ppscout_control.base import BaseController

__all__ = [
    'ARM_JOINTS',
    'GRIPPER_CLOSED',
    'GRIPPER_OPEN',
    'JOINT_LIMITS',
    'NAMED_POSES',
    'ArmController',
    'BaseController',
]
