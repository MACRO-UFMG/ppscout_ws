"""Move the Piper arm to a named pose or explicit joint positions.

    ros2 run ppscout_control arm_pose home
    ros2 run ppscout_control arm_pose ready --time 4
    ros2 run ppscout_control arm_pose -- 0.5 1.0 -1.0 0.0 0.5 0.0
"""

import argparse
import sys

import rclpy

from ppscout_control.arm import NAMED_POSES, ArmController


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pose', nargs='+',
                        help=f'named pose ({", ".join(sorted(NAMED_POSES))}) '
                             'or 6 joint positions in radians')
    parser.add_argument('--time', type=float, default=3.0,
                        help='trajectory duration in seconds (default 3)')
    args = parser.parse_args(argv)

    if len(args.pose) == 1 and not _is_number(args.pose[0]):
        name = args.pose[0]
        if name not in NAMED_POSES:
            parser.error(f'unknown pose {name!r}; '
                         f'available: {", ".join(sorted(NAMED_POSES))}')
        positions = NAMED_POSES[name]
    elif len(args.pose) == 6:
        try:
            positions = [float(v) for v in args.pose]
        except ValueError:
            parser.error('joint positions must be numbers')
    else:
        parser.error('give one named pose or exactly 6 joint positions')

    rclpy.init()
    arm = ArmController()
    try:
        if not arm.wait_until_ready():
            return 1
        arm.get_logger().info(f'Moving to {positions} over {args.time} s')
        ok = arm.move_joints(positions, duration=args.time)
        arm.get_logger().info('Done' if ok else 'Failed')
        return 0 if ok else 1
    finally:
        arm.destroy_node()
        rclpy.shutdown()


def _is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    sys.exit(main())
