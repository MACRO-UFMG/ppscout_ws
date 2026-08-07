"""End-to-end demo: move the arm, work the gripper, drive a small square.

Run the simulation first (ros2 launch ppscout_bringup sim.launch.py), then:

    ros2 run ppscout_control demo
"""

import argparse
import math
import sys

import rclpy

from ppscout_control.arm import ArmController
from ppscout_control.base import BaseController


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-drive', action='store_true',
                        help='only run the arm/gripper part of the demo')
    parser.add_argument('--side', type=float, default=1.0,
                        help='side length of the driven square in meters (default 1)')
    args = parser.parse_args(argv)

    rclpy.init()
    arm = ArmController()
    base = BaseController()
    try:
        log = arm.get_logger()

        log.info('Waiting for arm controllers...')
        if not arm.wait_until_ready():
            return 1

        log.info('Arm to ready pose')
        arm.move_named('ready')

        log.info('Closing and opening gripper')
        arm.close_gripper()
        rclpy.spin_once(arm, timeout_sec=2.0)
        arm.open_gripper()
        rclpy.spin_once(arm, timeout_sec=2.0)

        if not args.skip_drive:
            log.info(f'Driving a {args.side} m square')
            for _ in range(4):
                base.move_straight(args.side, speed=0.3)
                base.turn(math.pi / 2, angular_speed=0.5)

        log.info('Arm back to home')
        arm.home()

        log.info('Demo complete')
        return 0
    finally:
        base.stop()
        arm.destroy_node()
        base.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
