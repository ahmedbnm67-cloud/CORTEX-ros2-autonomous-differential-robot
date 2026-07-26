#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from  sensor_msgs.msg import LaserScan

class LidarRepublisher(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("lidar_republisher") # MODIFY NAME
        self.old_imu_sub = self.create_subscription(LaserScan , "/scan" , self.callback_lidar , 10)
        self.new_imu_pub = self.create_publisher(LaserScan , "/cortex/scan" , 10)

    def callback_lidar (self , msg: LaserScan): 
        msg.header.frame_id = "lidar_link"

        self.new_imu_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LidarRepublisher() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()