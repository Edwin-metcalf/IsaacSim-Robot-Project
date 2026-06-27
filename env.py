import numpy as np
from isaacsim.core.api import World
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
#from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path

#default cube settings
CUBE_COLORS = {
        "red": np.array([1.0, 0.0, 0.0]),
        "yellow": np.array([1.0, 1.0, 0.0]),
        "green": np.array([0.0, 0.9, 0.0]),
        }

DEFAULT_CUBE_POSITIONS = {
        "red": np.array([0.3, 0.0, 0.05]),
        "yellow": np.array([0.3, 0.2, 0.05]),
        "green": np.array([0.3, -0.2, 0.05]),
        }

def setup_scene(cube_positions=None):
    if cube_positions is None:
        cube_positions = DEFAULT_CUBE_POSITIONS 

    world = World()
    world.scene.add_default_ground_plane()

    # load up the franka bot1
    franka = world.scene.add(
            Franka(prim_path="/World/Franka", name="franka")
            )


    #set up the cubes 
    cubes = {}
    for color, position in cube_positions.items():
        cube = world.scene.add(
                DynamicCuboid(
                    prim_path=f"/World/{color.capitalize()}Cube",
                    name=f"{color}_cube",
                    position=position,
                    scale=np.array([0.05, 0.05, 0.05]),
                    color=CUBE_COLORS[color]
                )
            )
        cubes[color] = cube

    world.reset()

    return world, franka, cubes


def randomize_cube_positions(rng=None):
    #random positions ie in front of robot and far enough apart
    if rng is None:
        rng = np.random.default_rng()

    colors = list(CUBE_COLORS.keys())
    positions = {}
    placed = []

    for color in colors:
        while True:
            x = rng.uniform(0.25, 0.45)
            y = rng.uniform(-0.3, 0.3)
            pos = np.array([x, y, 0.05])

            too_close = any(
                    np.linalg.norm(pos[:2] - p[:2]) < 0.12
                    for p in placed
                    )
            if not too_close:
                positions[color] = pos 
                placed.append(pos)
                break

    return positions
if __name__ == "__main__":
    world, franka = setup_scene()
    print("scene setup OK")
    print(f"Franka loaded: {world.scene.object_exists('franka')}")
    print(f"Franka DOF count: {franka.num_dof}")
    print(f"Cube loaded: {world.scene.object_exists('pick_cube')}")
    cube_pos, _ = cube.get_world_pose()
    print(f"Cube position: {cube_pos}")


