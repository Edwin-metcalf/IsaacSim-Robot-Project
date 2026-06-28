import numpy as np
from controller import make_controller, move_to_target, open_gripper, close_gripper

#fixed distances in meters1
GRASP_HEIGHT_OFFSET = 0.15
LIFT_HEIGHT = 0.3
PLACE_POSITION_FIXED = np.array([0.3, -0.3, 0.05])

def run_pick_and_place(world, franka, cube, place_position=None):
    #tell the franka to pick and place and return dict for eval
    if place_position is None:
        place_position = PLACE_POSITION_FIXED

    controller, art_controller = make_controller(franka)

    cube_pos, _ = cube.get_world_pose()
    print(f"[task] Cube at: {np.round(cube_pos, 3)}")

    result = { 
              "cube_start": cube_pos.copy(),
              "phases": {}
              }

    print("[task] phase1: move towards cube")
    pre_grasp_pos = cube_pos.copy()
    pre_grasp_pos[2] += GRASP_HEIGHT_OFFSET

    success, dist, steps = move_to_target(
            world, franka, controller, art_controller, target_pos=pre_grasp_pos, threshold=0.06
            )
    result["phases"]["pre_grasp"] = {"success": success, "final_dist_m": round(dist, 4), "steps": steps}
    print(f"[task]   -> {'OK' if success else 'FAILED'} in {steps} steps, dist={dist:.4f}m")

    
    print("[task] Phase 2: lowering to grasp")
    grasp_pos = cube_pos.copy()
    grasp_pos[2] += 0.02 #get it to the right spot to close around cube

    success, dist, steps = move_to_target(
            world, franka, controller, art_controller, target_pos=grasp_pos, threshold=0.06
            )
    result["phases"]["grasp_approach"] = {"success": success, "final_dist_m": round(dist, 4), "steps": steps}
    print(f"[task]   -> {'OK' if success else 'FAILED'} in {steps} steps, dist={dist:.4f}m")

    print("[task] Phase 3: close gripper")
    close_gripper(franka)

    #use Kinematic overide to grab the cube
    cube.prim.GetAttribute("physics:collisionEnabled").Set(False)
    cube.prim.GetAttribute("physics:kinematicEnabled").Set(True)


    #for bug perposes let physics run a couple times
    for _ in range(30):
        world.step(render=False)
        ee_pos, ee_ori = franka.end_effector.get_world_pose()
        cube.set_world_pose(position=ee_pos, orientation=ee_ori)

    result["phases"]["grasp"] = {"success": True}


    print("[task] phase 4: lift the cube up")
    lift_pos = cube_pos.copy()
    lift_pos[2] = LIFT_HEIGHT

    success, dist, steps = move_to_target(
            world, franka, controller, art_controller, target_pos=lift_pos,
            attached_object=cube
            )

    #check if we are still holding on to the cube
    cube_pos_after_lift, _ = cube.get_world_pose()
    cube_lifted = cube_pos_after_lift[2] > 0.1
    result["phases"]["lift"] = {
        "success": success,
        "cube_lifted": bool(cube_lifted),
        "cube_z": round(float(cube_pos_after_lift[2]), 4),
        "steps": steps
    }
    print(f"[task]   -> EE {'OK' if success else 'FAILED'}, cube z={cube_pos_after_lift[2]:.3f}m ({'LIFTED' if cube_lifted else 'DROPPED'})")

    print("[task] phase 5: move with the cube")
    success, dist, steps = move_to_target(
            world, franka, controller, art_controller, 
            target_pos=place_position + np.array([0, 0, LIFT_HEIGHT]),
            attached_object=cube, threshold=0.05
            )
    result["phases"]["transport"] = {"success": success, "final_dist_m": round(dist, 4), "steps": steps}
    print(f"[task]   -> {'OK' if success else 'FAILED'} in {steps} steps")

    
    print("[task] phase 6: drop the cube")

    #move to right above ground to try and get close to correct landing
    #more of a place then a drop to try and be more accurate

    hover_pos = place_position.copy()
    hover_pos[2] += 0.03

    move_to_target(world, franka, controller, art_controller,
                   target_pos=hover_pos,
                   attached_object=cube,
                   threshold=0.02
                   )

    open_gripper(franka)

    # park the cube and stop moving so no left over velo
    for _ in range(20):
        world.step(render=False)
        ee_pos, ee_ori = franka.end_effector.get_world_pose()
        cube.set_world_pose(position=ee_pos, orientation=ee_ori)

    """
    final_ee_pos, final_ee_ori = franka.end_effector.get_world_pose()
    release_pos = np.array([
        place_position[0],
        place_position[1],
        final_ee_pos[2]
        ])

    cube.set_world_pose(position=release_pos, orientation=final_ee_ori)
    """
    #got to disable our kinematic override
    cube.prim.GetAttribute("physics:collisionEnabled").Set(True)
    cube.prim.GetAttribute("physics:kinematicEnabled").Set(False)
    cube.set_linear_velocity(np.array([0.0, 0.0, 0.0]))
    cube.set_angular_velocity(np.array([0.0, 0.0, 0.0]))

    for _ in range(60):
        world.step(render=False)


    cube_pos_after_reenable, _ = cube.get_world_pose()
    print(f"[DEBUG] Cube position after physics re-enable: {np.round(cube_pos_after_reenable, 3)}")


    #open_gripper(franka)
    for _ in range(60):
        world.step(render=False)


    #check if the cube is by the place target
    cube_final_pos, _ = cube.get_world_pose()
    xy_error = np.linalg.norm(cube_final_pos[:2] - place_position[:2])
    place_success= xy_error < 0.1

    result["phases"]["place"] = {
        "success": bool(place_success),
        "cube_final_pos": cube_final_pos.tolist(),
        "xy_error_m": round(float(xy_error), 4)
    }
    result["overall_success"] = bool(place_success and cube_lifted)

    print(f"[task] Phase 6: cube landed at {np.round(cube_final_pos, 3)}, XY error={xy_error:.3f}m")
    print(f"[task] OVERALL: {'SUCCESS' if result['overall_success'] else 'FAILURE'}")

    return result





