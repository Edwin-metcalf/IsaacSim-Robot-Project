from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
import numpy as np

world, franka, cube = setup_scene()
world.step(render=False)
print("=" * 40)
print("SCENE SETUP OK")
print("=" * 40)
print(f"Franka loaded:    {world.scene.object_exists('franka')}")
print(f"Franka DOF count: {franka.num_dof}")
print(f"Cube loaded:      {world.scene.object_exists('pick_cube')}")

cube_pos, _ = cube.get_world_pose()
print(f"Cube position:    {np.round(cube_pos, 4)}")

ee_pos, _ = franka.end_effector.get_world_pose()
print(f"End effector pos: {np.round(ee_pos, 4)}")

dist = np.linalg.norm(ee_pos - cube_pos)
print(f"EE → Cube dist:   {dist:.4f} m")
print("=" * 40)

app.close()
