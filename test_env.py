from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
import numpy as np

world, franka, cubes = setup_scene()
world.step(render=False)

ee_pos, _ = franka.end_effector.get_world_pose()

print("=" * 40)
print("SCENE SETUP OK")
print("=" * 40)
print(f"Franka loaded:    {world.scene.object_exists('franka')}")
print(f"Franka DOF count: {franka.num_dof}")

for color, cube in cubes.items():
    exists = world.scene.object_exists(f"{color}_cube")
    cube_pos, _ = cube.get_world_pose()
    dist = np.linalg.norm(ee_pos - cube_pos)
    print(f"[{color.upper():6}] loaded={exists}  pos={np.round(cube_pos, 4)}  EE→cube dist={dist:.4f}m")

print()
print(f"End effector pos: {np.round(ee_pos, 4)}")
print("=" * 40)

app.close()
