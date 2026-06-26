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
                   target_pos, max_steps=1500, threshold=0.05):

    target_orientation = euler_angles_to_quats([0, np.pi, 0])

    print(f"FRANKA END EFFECTOR NAME and PATH: {franka.end_effector.name}")
    print(franka.end_effector.prim_path)

    for i in range(max_steps):
        world.step(render=False)

        actions = controller.forward(
            target_end_effector_position=target_pos,
            target_end_effector_orientation=target_orientation
        )
        if i == 0:
            print(actions)
            print(actions.joint_positions)

        art_controller.apply_action(actions)

        ee_pos, ee_ori = franka.end_effector.get_world_pose()
        dist = np.linalg.norm(ee_pos - target_pos)

        if i == 300:
            print("\n=== Settled State ===")
            print("EE Position:", np.round(ee_pos, 3))
            print("EE Orientation:", np.round(ee_ori, 4))
            print("Target Position:", np.round(target_pos, 3))
            print("Current joints:", np.round(franka.get_joint_positions()[:7], 3))
            print("Commanded joints:", np.round(actions.joint_positions, 3))
        if dist < threshold:
            return True, dist, i

    ee_pos, _ = franka.end_effector.get_world_pose()
    return False, np.linalg.norm(ee_pos - target_pos), max_steps


def open_gripper(franka):
    franka.gripper.open()


def close_gripper(franka):
    franka.gripper.close()
