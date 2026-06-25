from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

import numpy as np
from isaacsim.core.api import World
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.storage.native import get_assets_root_path


def setup_scene():
    world = World()
    world.scene.add_default_ground_plane()

    assets_root = get_assets_root_path()
    franka_path = assets_root + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
    add_reference_to_stage(usd_path=franka_path, prim_path="/World/Franka")

    franka = world.scene.add(Robot(prim_path="/World/Franka", name="franka"))

    world.reset()

    return world, franka

if __name__ == "__main__":
    world, franka = setup_scene()
    print("scene setup OK")
    print(f"Franka loaded: {world.scene.object_exists('franka')}")
    print(f"Franka DOF count: {franka.num_dof}")
    app.close()
