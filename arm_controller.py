#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String

POSITIONS = {
    "HOME":  [0.0,   0.0,  0.0,  0.3, -0.3],
    "REACH": [-0.6,  0.6,  0.5,  0.3, -0.3],
    "GRIP":  [-0.6,  0.6,  0.5,  0.0,  0.0],
    "LIFT":  [-0.6,  0.3,  0.2,  0.0,  0.0],
    "MOVE":  [0.6,   0.3,  0.2,  0.0,  0.0],
    "PLACE": [0.6,   0.6,  0.5,  0.0,  0.0],
    "OPEN":  [0.6,   0.6,  0.5,  0.3, -0.3],
}
DWELL_TIME = {
    "HOME":  2.0, "REACH": 2.5, "GRIP": 1.5,
    "LIFT":  2.0, "MOVE":  2.5, "PLACE": 2.0, "OPEN": 1.5,
}
STATE_SEQUENCE = ["HOME", "REACH", "GRIP", "LIFT", "MOVE", "PLACE", "OPEN"]

class ArmController(Node):
    def __init__(self):
        super().__init__("arm_controller")
        self.joint_pub = self.create_publisher(Float64MultiArray, "/arm/joint_commands", 10)
        self.state_pub = self.create_publisher(String, "/arm/current_state", 10)
        self.state_index = 0
        self.cycle_count = 0
        self.state_start_time = None
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("ArmController started.")

    def publish_joint_positions(self, state_name):
        msg = Float64MultiArray()
        msg.data = POSITIONS[state_name]
        self.joint_pub.publish(msg)

    def publish_current_state(self, state_name):
        msg = String()
        msg.data = state_name
        self.state_pub.publish(msg)

    def control_loop(self):
        current_state = STATE_SEQUENCE[self.state_index]
        if self.state_start_time is None:
            self.state_start_time = self.get_clock().now()
            self.get_logger().info(f"State: {current_state} | Cycle: {self.cycle_count + 1}")
        self.publish_joint_positions(current_state)
        self.publish_current_state(current_state)
        elapsed = (self.get_clock().now() - self.state_start_time).nanoseconds / 1e9
        if elapsed >= DWELL_TIME[current_state]:
            self.state_index += 1
            self.state_start_time = None
            if self.state_index >= len(STATE_SEQUENCE):
                self.state_index = 0
                self.cycle_count += 1
                self.get_logger().info(f"Cycle {self.cycle_count} complete. Restarting.")

def main(args=None):
    rclpy.init(args=args)
    node = ArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
