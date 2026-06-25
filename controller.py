import numpy as np


def make_controller(franka, world):
    from isaacsim.robot_motion.motion_generation import ArticulationMotionPolicy, RmpFlow
    from isaacsim.robot_motion.motion_generation.interface_config_loader import load_supported_motion_policy_config

    rmp_config = load_supported_motion_policy_config("Franka", "RMPflow")
    rmpflow = RmpFlow(**rmp_config)
    articulation_rmpflow = ArticulationMotionPolicy(franka, rmpflow)
    return rmpflow, articulation_rmpflow

def move_to_target(world, franka, rmpflow, articulation_rmpflow, target_pos, max_steps=1500, threshold=0.02):
    from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats
    target_orientation = euler_angles_to_quats([0, np.pi, 0])

    step_size = 1.0/60.0

    for i in range(max_steps):
        rmpflow.set_end_effector_target(target_pos, target_orientation)

        base_pos, base_ori = franka.get_world_pose()
        rmpflow.set_robot_base_pose(base_pos, base_ori)
        rmpflow.update_world()

        action = articulation_rmpflow.get_next_articulation_action(step_size)
        franka.apply_action(action)

        world.step(render=False) 
        
        ee_pos, _ = franka.end_effector.get_world_pose()
        dist = np.linalg.norm(ee_pos - target_pos)

        if dist < threshold:
            return True, dist, i
    
    ee_pos, _ = franka.end_effector.get_world_pose()
    final_dist = np.linalg.norm(ee_pos - target_pos)
    return False, final_dist, max_steps

def open_gripper(franka):
    franka.gripper.open()

def close_gripper(franka):
    franka.gripper.close()

