import os 
import json
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"

def build_scene_description(cubes: dict) -> str:
    """ this scene takes in 3 different color cubes """
    lines = ["scene containes the following cubes:"]
    for color, pos in cubes.items():
        lines.append(f" - {color} cube at position x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")

    return "\n".join(lines)

def query_vlm(task_instruction: str, cubes: dict) -> dict:
    # returns query pick color and position of that cube and place 

    scene_desc = build_scene_description(cubes)

    prompt = f"""{scene_desc}

    Task instruction: "{task_instruction}"

    You are a robot task planner. Based on the scene and instruction, identify:
    1. Which cube to pick up (the source)
    2. Which cube to place it on (the destination)

    Respond with ONLY a JSON object in this exact format, no other text:
    {{
      "pick_color": "<color>",
      "pick_pos": [x, y, z],
      "place_color": "<color>",
      "place_pos": [x, y, z],
      "reasoning": "<one sentence>"
    }}"""

    headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
            }

    body = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": prompt}]
            }
    response = requests.post(API_URL, headers=headers, json=body, timeout=15)
    response.raise_for_status()

    raw = response.json()["content"][0]["text"].strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    plan = json.loads(raw.strip())
    return plan



if __name__ == "__main__":
    # quick smoke test without Isaac Sim
    import numpy as np
    test_cubes = {
        "red":    np.array([0.3,  0.0,  0.05]),
        "yellow": np.array([0.3,  0.2,  0.05]),
        "green":  np.array([0.3, -0.2,  0.05]),
    }
    result = query_vlm("pick up the yellow cube and place it on the red cube", test_cubes)
    print(json.dumps(result, indent=2))
