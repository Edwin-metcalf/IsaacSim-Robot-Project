import numpy as np
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats
from isaacsim.robot.manipulators.examples.franka.controllers.rmpflow_controller import RMPFlowController


def make_controller(franka):
    controller = RMPFlowController(
        name="rmpflow_controller",
        robot_articulation=franka
    )
    art_controller = franka.get_articulation_controller()
    return controller, art_controller


def move_to_target(world, franka, controller, art_controller,
                   target_pos, max_steps=1500, threshold=0.02):

    target_orientation = euler_angles_to_quats([0, np.pi, 0])

    for i in range(max_steps):
        world.step(render=False)

        actions = controller.forward(
            target_end_effector_position=target_pos,
            target_end_effector_orientation=target_orientation
        )
        art_controller.apply_action(actions)

        ee_pos, _ = franka.end_effector.get_world_pose()
        dist = np.linalg.norm(ee_pos - target_pos)
        if dist < threshold:
            return True, dist, i

    ee_pos, _ = franka.end_effector.get_world_pose()
    return False, np.linalg.norm(ee_pos - target_pos), max_steps


def open_gripper(franka):
    franka.gripper.open()


def close_gripper(franka):
    franka.gripper.close()
