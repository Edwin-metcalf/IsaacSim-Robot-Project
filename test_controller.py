from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
from controller import make_controller

world, franka = setup_scene()
rmpflow, articulation_rmpflow = make_controller(franka, world)
print("controller init OK")
print(f"RMPflow  type: {type(rmpflow)}")

app.close()
