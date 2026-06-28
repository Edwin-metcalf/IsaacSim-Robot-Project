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


def move_to_target(world, articulation, rmpflow, articulation_rmpflow,
                   target_pos, max_steps=1500, threshold=0.05, 
                   attached_object=None):
    rmpflow.reset()
    target_orientation = euler_angles_to_quats([0, np.pi, 0])

    #print(f"FRANKA END EFFECTOR NAME and PATH: {articulation.end_effector.name}")
    #print(articulation.end_effector.prim_path)

    for i in range(max_steps):
        world.step(render=False)
        step_size = 1.0/60.0
        
        #simulating a grab attach the item and turn its physics off essentially
        if attached_object is not None:
            ee_pos, ee_ori = articulation.end_effector.get_world_pose()
            attached_object.set_world_pose(position=ee_pos, orientation=ee_ori)
            #attached_object.set_linear_velocity(np.array([0.0, 0.0, 0.0]))
            #attached_object.set_angular_velocity(np.array([0.0, 0.0, 0.0]))

        action = rmpflow.forward(
                target_end_effector_position=target_pos,
                target_end_effector_orientation=target_orientation
                )

        articulation.apply_action(action)

        #if i == 0:
            #print(action)

        ee_pos, _ = articulation.end_effector.get_world_pose()
        dist = np.linalg.norm(ee_pos - target_pos)
        """
        if i == 300:
            print("\n=== Settled State ===")
            print("EE Position:", np.round(ee_pos, 3))
            #print("EE Orientation:", np.round(ee_ori, 4))
            print("Target Position:", np.round(target_pos, 3))
            print("Current joints:", np.round(articulation.get_joint_positions()[:7], 3))
            print("Commanded joints:", np.round(action.joint_positions, 3))

            if action.joint_positions is not None:
                print("Commanded joints:", np.round(action.joint_positions, 3))
        """
        if dist < threshold:
            return True, dist, i

    ee_pos, _ = articulation.end_effector.get_world_pose()
    final_dist = np.linalg.norm(ee_pos - target_pos)
    return False, final_dist, max_steps


def open_gripper(franka):
    franka.gripper.open()


def close_gripper(franka):
    franka.gripper.close()
