import numpy as np
from isaacsim.core.api import World
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
#from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path


def setup_scene(cube_position=None):
    if cube_position is None:
        cube_position = np.array([0.3, 0.0, 0.05])

    world = World()
    world.scene.add_default_ground_plane()

    # load up the franka bot1
    franka = world.scene.add(
            Franka(prim_path="/World/Franka", name="franka")
            )


    # create a cube for the bot to pick up
    cube = world.scene.add(
            DynamicCuboid(
                prim_path="/World/PickCube",
                name="pick_cube",
                scale=np.array([0.05, 0.05, 0.05])
                )
            )
    world.reset()

    return world, franka, cube

if __name__ == "__main__":
    world, franka = setup_scene()
    print("scene setup OK")
    print(f"Franka loaded: {world.scene.object_exists('franka')}")
    print(f"Franka DOF count: {franka.num_dof}")
    print(f"Cube loaded: {world.scene.object_exists('pick_cube')}")
    cube_pos, _ = cube.get_world_pose()
    print(f"Cube position: {cube_pos}")


