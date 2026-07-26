#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuRepublisher(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("imu_republisher") # MODIFY NAME
        self.old_imu_sub = self.create_subscription(Imu , "/imu" , self.callback_imu , 10)
        self.new_imu_pub = self.create_publisher(Imu , "/cortex/imu" , 10)

    def callback_imu (self , msg: Imu): 
        msg.header.frame_id = "base_footprint_ekf"

        self.new_imu_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuRepublisher() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()