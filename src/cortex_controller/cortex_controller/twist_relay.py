#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

"""
Joystick
--------
JoyTeleop
    /input_joy/cmd_vel_stamped (TwistStamped)
        ↓
TwistRelay
    /input_joy/cmd_vel (Twist)
        ↓
TwistMux
    /explorer/cmd_vel_unstamped (Twist)
        ↓
TwistRelay
    /explorer/cmd_vel (TwistStamped)
        ↓
Robot Controller
"""


class TwistRelay(Node):

    def __init__(self):
        super().__init__("twist_relay")

        # Joy -> Twist
        self.joy_sub = self.create_subscription(
            TwistStamped,
            "/input_joy/cmd_vel_stamped",
            self.callback_joy,
            10
        )

        self.joy_pub = self.create_publisher(
            Twist,
            "/input_joy/cmd_vel",
            10
        )

        # TwistMux -> Controller
        self.controller_sub = self.create_subscription(
            Twist,
            "/cortex/cmd_vel_unstamped",
            self.callback_cmd,
            10
        )

        self.controller_pub = self.create_publisher(
            TwistStamped,
            "/cortex/cmd_vel",
            10
        )

    def callback_joy(self, msg: TwistStamped):
        self.joy_pub.publish(msg.twist)

    def callback_cmd(self, msg: Twist):
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.twist = msg
        self.controller_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)

    node = TwistRelay()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()