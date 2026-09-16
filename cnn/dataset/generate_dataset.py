from issaacsim import SimulationApp
import os
import random

app = SimulationApp() 

from env import setup_scene, randomize_cube_positions
_, _, _ = setup_scene()

# creating the camera
camera = rep.functional.create.camera(name="Camera")
#count is to make all the names unique
count = 0

try: 
    os.mkdir("/data")
    print("/data created successfully")
except FileExistsError:
    ("/data already exists")
except OSError as e:
    print(f"directory creation failed: {e}")

target_color = random.choice(
    ["red", "yellow", "green"]
)
screenshot = camera.get_rgb()
with open("/data/"+ target_color + "/" + count + ".png") as file:



