#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.constants import S_TO_NS
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from tf_transformations import quaternion_from_euler
from tf2_ros.transform_broadcaster import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import numpy as np
import math

class CortexVelocityController(Node): # MODIFY NAME
    def __init__(self):
        super().__init__("cortex_velocity_controller") # MODIFY NAME

        self.declare_parameter("wheel_radius" , 0.034)
        self.declare_parameter("wheel_seperation" , 0.301)
        self.declare_parameter("wheel_radius_errro" , 0.002)
        self.wheel_radius = self.get_parameter("wheel_radius").value + self.get_parameter("wheel_radius_errro").value
        self.wheel_seperation = self.get_parameter("wheel_seperation").value

        self.prev_position_left = 0.0
        self.prev_position_right = 0.0
        self.prev_time = self.get_clock().now()

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    
        self.odom_pub = self.create_publisher(Odometry , "/cortex/odom_noise" , 10)
        self.joint_state_sub = self.create_subscription(JointState , "/joint_states" , self.callback_jointstate , 10)

        self.dynamic_transformer_broadcaster =TransformBroadcaster(self)

        self.dynamic_transformer_stamped = TransformStamped()
        self.dynamic_transformer_stamped.header.frame_id = "odom"
        self.dynamic_transformer_stamped.child_frame_id = "base_footprint_noise"

        self.odom = Odometry()
        self.odom.header.frame_id = "odom"
        self.odom.child_frame_id = "base_footprint_ekf"
        
    def callback_jointstate(self , msg:JointState):
        left_wheel_pose  = msg.position[0] + np.random.normal(0.00 , 0.005)
        right_wheel_pose = msg.position[1] + np.random.normal(0.00 , 0.005)
        dp_left  = left_wheel_pose  - self.prev_position_left
        dp_right = right_wheel_pose - self.prev_position_right
        current_time = Time.from_msg(msg.header.stamp)
        dt = (current_time - self.prev_time).nanoseconds / 1e9

        self.prev_position_left = msg.position[0]
        self.prev_position_right = msg.position[1]
        self.prev_time = current_time

        #wheels velocitys in rad / second
        fi_left = (dp_left / dt)
        fi_right = (dp_right / dt)

        #robot velocity 
        linear = (self.wheel_radius * fi_right + self.wheel_radius * fi_left ) / 2.0
        anguler =(self.wheel_radius * fi_right - self.wheel_radius * fi_left ) / self.wheel_seperation

        d_theta = (self.wheel_radius * dp_right - self.wheel_radius * dp_left ) / self.wheel_seperation
        ds_vector = (self.wheel_radius * dp_right + self.wheel_radius * dp_left ) / 2.0

        self.theta += d_theta
        self.x += ds_vector * math.cos(self.theta)
        self.y += ds_vector * math.sin(self.theta)
        q = quaternion_from_euler(0.0 , 0.0 ,self.theta)

        self.odom.header.stamp = self.get_clock().now().to_msg()
        self.odom.pose.pose.position.x = self.x
        self.odom.pose.pose.position.y = self.y
        self.odom.pose.pose.position.z = 0.0
        self.odom.pose.pose.orientation.x = q[0]
        self.odom.pose.pose.orientation.y = q[1]
        self.odom.pose.pose.orientation.z = q[2]
        self.odom.pose.pose.orientation.w = q[3]
        self.odom.twist.twist.linear.x = linear
        self.odom.twist.twist.angular.z = anguler


        self.dynamic_transformer_stamped.header.stamp = self.get_clock().now().to_msg()
        self.dynamic_transformer_stamped.transform.translation.x = self.x
        self.dynamic_transformer_stamped.transform.translation.y = self.y
        self.dynamic_transformer_stamped.transform.translation.z = 0.0
        self.dynamic_transformer_stamped.transform.rotation.x = q[0]
        self.dynamic_transformer_stamped.transform.rotation.y = q[1]
        self.dynamic_transformer_stamped.transform.rotation.z = q[2]
        self.dynamic_transformer_stamped.transform.rotation.w = q[3]

        self.odom_pub.publish(self.odom)
        self.dynamic_transformer_broadcaster.sendTransform(self.dynamic_transformer_stamped)

def main(args=None):
    rclpy.init(args=args)
    node = CortexVelocityController() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()