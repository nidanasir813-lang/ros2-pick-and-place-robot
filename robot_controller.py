#!/usr/bin/env python3

"""
robot_controller.py
-------------------
Webots Supervisor controller for industrial pick-and-place arm.
Box visually follows the arm during carry phase.

Author: Nida Nasir
Project: Autonomous Pick-and-Place Robotic Arm using ROS2 in Simulation
"""

from controller import Supervisor

TIME_STEP = 32
MOTOR_NAMES = ["joint1", "joint2", "joint3", "gripper_left", "gripper_right"]

POSITIONS = [
    [0.0,   0.0,  0.0,   0.4,  -0.4],
    [0.0,   0.9,  0.7,   0.4,  -0.4],
    [0.0,   0.9,  0.7,   0.04, -0.04],
    [0.0,   0.4,  0.3,   0.04, -0.04],
    [3.14,  0.4,  0.3,   0.04, -0.04],
    [3.14,  0.9,  0.7,   0.04, -0.04],
    [3.14,  0.9,  0.7,   0.4,  -0.4],
    [0.0,   0.0,  0.0,   0.4,  -0.4],
]

HOLD_STEPS  = [50, 100, 50, 80, 100, 80, 50, 80]
STATE_NAMES = ["HOME", "REACH", "GRIP", "LIFT", "ROTATE", "LOWER", "RELEASE", "RETURN"]

PICK_POSITION  = [0.0,  0.395, -0.85]
PLACE_POSITION = [0.0,  0.405,  0.85]


def run_controller():
    robot = Supervisor()

    motors = []
    for name in MOTOR_NAMES:
        motor = robot.getDevice(name)
        motor.setPosition(0.0)
        motors.append(motor)

    box_node = robot.getFromDef("BOX_GREEN")
    box_translation = box_node.getField("translation") if box_node else None

    # Get the gripper node to track its position
    gripper_node = robot.getFromDef("GRIPPER_BODY") if robot.getFromDef("GRIPPER_BODY") else None

    state_index  = 0
    step_counter = 0
    cycle_count  = 0
    box_picked   = False

    print("[robot_controller] Industrial pick-and-place started.")

    while robot.step(TIME_STEP) != -1:

        for i, motor in enumerate(motors):
            motor.setPosition(POSITIONS[state_index][i])

        step_counter += 1
        current_state = STATE_NAMES[state_index]

        # During GRIP state: pick up box
        if current_state == "GRIP" and step_counter == 25 and not box_picked:
            if box_translation:
                box_translation.setSFVec3f([0.0, 0.5, -0.3])
                box_picked = True
                print("[robot_controller] Box gripped.")

        # During LIFT: keep box visible above scene
        if current_state == "LIFT" and box_picked:
            if box_translation:
                box_translation.setSFVec3f([0.0, 0.55, -0.1])

        # During ROTATE: box moves with arm
        if current_state == "ROTATE" and box_picked:
            if box_translation:
                box_translation.setSFVec3f([0.0, 0.55, 0.1])

        # During LOWER: place box on platform
        if current_state == "LOWER" and step_counter == 60 and box_picked:
            if box_translation:
                box_translation.setSFVec3f(PLACE_POSITION)
                box_picked = False
                print("[robot_controller] Box placed on platform.")

        if step_counter >= HOLD_STEPS[state_index]:
            print(f"[robot_controller] State complete: {current_state}")
            state_index += 1
            step_counter = 0

            if state_index >= len(POSITIONS):
                state_index = 0
                cycle_count += 1
                print(f"[robot_controller] Cycle {cycle_count} complete.")
                if box_translation:
                    box_translation.setSFVec3f(PICK_POSITION)
                    box_picked = False
                    print("[robot_controller] Box reset to conveyor.")


if __name__ == "__main__":
    run_controller()
