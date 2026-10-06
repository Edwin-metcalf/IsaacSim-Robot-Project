from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
from controller import make_controller

world, franka, cubes = setup_scene()
rmpflow, art_controller = make_controller(franka)
print("controller init OK")
print(f"RMPflow  type: {type(rmpflow)}")

app.close()
