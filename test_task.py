from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

from env import setup_scene
from task import run_pick_and_place 

world, franka, cube = setup_scene()
world.step(render=False)

result = run_pick_and_place(world, franka, cube)


print("\n--- RESULT DICT ---")
for phase, data in result["phases"].items():
    print(f"  {phase}: {data}")
print(f"  overall_success: {result['overall_success']}")

app.close()
