# debug_motion.py  - run this first to isolate the problem
from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
from isaacsim.robot_motion.motion_generation import ArticulationMotionPolicy, RmpFlow
from isaacsim.robot_motion.motion_generation.interface_config_loader import load_supported_motion_policy_config
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats
import numpy as np

world, franka, cube = setup_scene()
world.step(render=False)

# Build controller
rmp_config = load_supported_motion_policy_config("Franka", "RMPflow")
rmpflow = RmpFlow(**rmp_config)
articulation_rmpflow = ArticulationMotionPolicy(franka, rmpflow)

# Get the articulation controller - this is the correct apply path
art_controller = franka.get_articulation_controller()

target_pos = np.array([0.4, 0.0, 0.3])
target_ori = euler_angles_to_quats([0, np.pi, 0])

print("Joint positions at start:", np.round(franka.get_joint_positions(), 3))
print(f"EE at start: {np.round(franka.end_effector.get_world_pose()[0], 3)}")
print(f"Target: {target_pos}")
print()

for i in range(10):
    rmpflow.set_end_effector_target(target_pos, target_ori)
    base_pos, base_ori = franka.get_world_pose()
    rmpflow.set_robot_base_pose(base_pos, base_ori)
    rmpflow.update_world()

    action = articulation_rmpflow.get_next_articulation_action(1/60.0)

    # Print what RMPflow is actually commanding on frame 0
    if i == 0:
        print(f"Action joint_positions: {np.round(action.joint_positions, 3)}")
        print(f"Action joint_velocities: {action.joint_velocities}")

    # Apply via articulation controller
    art_controller.apply_action(action)
    world.step(render=False)

print()
print(f"Joint positions after 10 steps: {np.round(franka.get_joint_positions(), 3)}")
print(f"EE after 10 steps: {np.round(franka.end_effector.get_world_pose()[0], 3)}")

app.close()
