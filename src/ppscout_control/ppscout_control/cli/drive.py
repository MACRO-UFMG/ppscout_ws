"""Drive the base at a constant velocity for a fixed time, then stop.

    ros2 run ppscout_control drive --linear 0.3 --duration 2
    ros2 run ppscout_control drive --angular 0.5 --duration 3
"""

import argparse

import rclpy

from ppscout_control.base import BaseController


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linear', type=float, default=0.0,
                        help='forward velocity in m/s (default 0)')
    parser.add_argument('--angular', type=float, default=0.0,
                        help='yaw rate in rad/s (default 0)')
    parser.add_argument('--duration', type=float, default=1.0,
                        help='how long to drive in seconds (default 1)')
    args = parser.parse_args(argv)

    rclpy.init()
    base = BaseController()
    try:
        base.get_logger().info(
            f'Driving linear={args.linear} m/s, angular={args.angular} rad/s '
            f'for {args.duration} s')
        base.drive(args.linear, args.angular, args.duration)
        base.get_logger().info('Stopped')
    finally:
        base.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
