"""Open, close, or set the gripper position.

    ros2 run ppscout_control gripper open
    ros2 run ppscout_control gripper close
    ros2 run ppscout_control gripper 0.05
"""

import argparse
import sys

import rclpy

from ppscout_control.arm import GRIPPER_CLOSED, GRIPPER_OPEN, ArmController


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',
                        help="'open', 'close', or a joint position in meters "
                             f'({GRIPPER_OPEN} = open, {GRIPPER_CLOSED} = closed)')
    args = parser.parse_args(argv)

    if args.command == 'open':
        position = GRIPPER_OPEN
    elif args.command == 'close':
        position = GRIPPER_CLOSED
    else:
        try:
            position = float(args.command)
        except ValueError:
            parser.error("command must be 'open', 'close', or a number")

    rclpy.init()
    arm = ArmController()
    try:
        arm.get_logger().info(f'Setting gripper to {position} m')
        arm.set_gripper(position)
        # give the publisher time to deliver before shutting down
        rclpy.spin_once(arm, timeout_sec=0.5)
    finally:
        arm.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
