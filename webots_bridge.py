#!/usr/bin/env python3

"""
webots_bridge.py
----------------
Subscribes to /arm/joint_commands and forwards each joint position
to individual motor topics for the Webots simulation.

Author: Nida Nasir
Project: Autonomous Pick-and-Place Robotic Arm using ROS2 in Simulation
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

JOINT_NAMES = ["joint1", "joint2", "joint3", "gripper_left", "gripper_right"]


class WebotsBridge(Node):
    def __init__(self):
        super().__init__("webots_bridge")
        self.motor_pubs = []
        for name in JOINT_NAMES:
            pub = self.create_publisher(Float64MultiArray, f"/kuka_arm/{name}/cmd", 10)
            self.motor_pubs.append(pub)
        self.subscription = self.create_subscription(
            Float64MultiArray, "/arm/joint_commands", self.on_joint_command, 10)
        self.get_logger().info("WebotsBridge ready. Listening on /arm/joint_commands.")

    def on_joint_command(self, msg):
        if len(msg.data) != len(JOINT_NAMES):
            self.get_logger().warn(f"Expected {len(JOINT_NAMES)} values, got {len(msg.data)}.")
            return
        for i, position in enumerate(msg.data):
            out_msg = Float64MultiArray()
            out_msg.data = [position]
            self.motor_pubs[i].publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = WebotsBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down WebotsBridge.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
