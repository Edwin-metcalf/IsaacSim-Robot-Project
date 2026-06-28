from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

import numpy as np
import json
from datetime import datetime

class NumpyEncoder(json.JSONEncoder):
    #turn numpy floats into python ones
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

from env import setup_scene, randomize_cube_positions
from task import run_pick_and_place
from vlm_planner import query_vlm

#trial configs
NUM_TRIALS = 5
TASK_PROMPT = "pick up the yellow cube and place it on top of the red cube"
CUBE_HEIGHT = 0.05
SEED = 42

rng = np.random.default_rng(SEED)
all_results = []

print("=" * 60)
print("VLM pick and place eval")
print(f"Task Prompt: {TASK_PROMPT}")
print(f"# of trials: {NUM_TRIALS}")
print("=" * 60)

# build the scene once and then reuse
cube_positions = randomize_cube_positions(rng=rng)
world, franka, cubes = setup_scene(cube_positions=cube_positions)
world.reset()
world.step(render=False)


for trial_idx in range(NUM_TRIALS):
    print()
    print(f"Trial {trial_idx + 1} / {NUM_TRIALS}")

    #randomize positions on all but first(scene creation randomizes them)
    if trial_idx > 0:
        new_positions = randomize_cube_positions(rng=rng)
        for color, pos in new_positions.items():
            cubes[color].set_world_pose(position=pos)

    for _ in range(30):
        world.step(render=False)

    settled_positions = {}
    for color, cube in cubes.items():
        pos, _ = cube.get_world_pose()
        settled_positions[color] = pos.copy()

    print("settled positions of cubes")
    for color, pos in settled_positions.items():
        print(f"{color:6}: {np.round(pos, 3)}")


    #query the VLM 
    print()
    print("[vlm] querying planner")
    try:
        plan = query_vlm(TASK_PROMPT, settled_positions)
        print(f"[vlm] pick={plan['pick_color']}  place_on={plan['place_color']}")
        print(f"[vlm] reasoning: {plan['reasoning']}")
        vlm_ok = True
    except Exception as e:
        print(f"[vlm] ERROR: {e}")
        vlm_ok = False
        all_results.append({
            "trial": trial_idx + 1,
            "vlm_ok": False,
            "error": str(e),
            "overall_success": False
            })

        continue


    # Check the vlm response
    pick_color = plan["pick_color"]
    place_color = plan["place_color"]

    if pick_color not in cubes or place_color not in cubes:
        print(f"VLM retuned unknown colors: {pick_color}, {place_color}")
        all_results.append({
            "trial": trial_idx + 1,
            "vlm_ok": False, 
            "error": f"unknown colors: {pick_color}, {place_color}",
            "overall_success": False
            })

        continue


    #compute positions model decides which and sim proveds where
    pick_pos = settled_positions[pick_color].copy()
    place_pos = settled_positions[place_color].copy()

    #want to try and stack need to incrase height then 
    place_target = place_pos.copy()
    place_target[2] += CUBE_HEIGHT

    print(f"\n[orchestrator] Pick target:  {np.round(pick_pos, 3)}")
    print(f"[orchestrator] Place target: {np.round(place_target, 3)}  (stacked on {place_color})")

    #run the robot action
    pick_cube = cubes[pick_color]
    place_cube = cubes[place_color]

    result = run_pick_and_place(
            world=world,
            franka=franka,
            cube=pick_cube,
            place_position=place_target
            )

    #evaluate how close the placed cube is to target and check if they arestacked
    picked_final, _ = pick_cube.get_world_pose()
    place_cube_pos, _ = place_cube.get_world_pose()

    xy_error = np.linalg.norm(picked_final[:2] - place_cube_pos[:2])

    z_stack = picked_final[2] - place_cube_pos[2]
    stacked = xy_error < 0.08 and 0.02 < z_stack < 0.10

    trial_result = {
        "trial":           trial_idx + 1,
        "vlm_ok":          True,
        "plan":            {"pick": pick_color, "place_on": place_color},
        "cube_positions":  {c: p.tolist() for c, p in settled_positions.items()},
        "pick_pos":        pick_pos.tolist(),
        "place_target":    place_target.tolist(),
        "picked_final":    picked_final.tolist(),
        "place_cube_pos":  place_cube_pos.tolist(),
        "xy_error_m":      round(float(xy_error), 4),
        "z_stack_m":       round(float(z_stack), 4),
        "stacked":         bool(stacked),
        "phases":          result.get("phases", {}),
        "overall_success": bool(stacked)
    }
    
    all_results.append(trial_result)

    print(f"\n[eval] Picked cube final pos:  {np.round(picked_final, 3)}")
    print(f"[eval] Place cube pos:         {np.round(place_cube_pos, 3)}")
    print(f"[eval] XY error: {xy_error:.4f}m   Z stack: {z_stack:.4f}m")
    print(f"[eval] Stacked: {'YES ✓' if stacked else 'NO ✗'}")


    #Summary of trials

    print()
    print("=" * 60)
    print("SUMMARY")
    print()

    successes = [r for r in all_results if r["overall_success"]]
    vlm_errors = [r for r in all_results if not r["vlm_ok"]]

    print(f"Trials run:      {NUM_TRIALS}")
    print(f"VLM errors:     {len(vlm_errors)}")
    print(f"stacked ok:     {len(successes)} / {NUM_TRIALS}")

    if successes:
        xy_errors = [r["xy_error_m"] for r in successes]
        z_stacks = [r["z_stack_m"] for r in successes]
        
        print(f"mean xy error: {np.mean(xy_errors):.4f}m (std {np.std(xy_errors):.4f}m)")
        print(f"Mean z stack:   {np.mean(z_stacks):.4f}m (std {np.std(z_stacks):.4f}m)")

        print(f"\nPer Trial breakdown: ")
        for r in all_results:
            if not r["vlm_ok"]:
                print(f"  Trial {r['trial']}: VLM ERROR - {r.get('error', '?')}")
            else:
                status = "✓ STACKED" if r["overall_success"] else "✗ FAILED "
                print(f"  Trial {r['trial']}: {status}  xy={r['xy_error_m']:.4f}m  z={r['z_stack_m']:.4f}m  plan={r['plan']}")

# save results to json

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"output/vlm_results_{timestamp}.json"
with open(output_file, "w") as f:
    json.dump(all_results, f, indent=2, cls=NumpyEncoder)

print()
print(f"Results saved to: {output_file}")

app.close()




