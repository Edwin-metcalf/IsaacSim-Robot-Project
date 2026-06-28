# Isaac Sim VLM Pick & Place 

A closed-loop evaluation framework for testing Vision Language Models on spatial reasoning and robotic manipulation tasks within NVIDIA Isaac Sim.

This project simulates a Franka Emika Panda arm adn promts an AI to reason about the scene, generate a pick and place plan, and execute it usign RMPFlow for smooth kinematics.


## Features
* **Zero Shot Model Planning** Uses and Anthropic model to parse natural language insructions and map them to physical coordinates
* **Closed Loop Physics** Built with Isaac Sim library (all headless), complete with collision detection, grasp physics, and realistic object dropping
* **Automated Evaluation** Runs multi-trial tests, trackign X/Y placement error, Z stacking success, and automated logging to JSON

---
## Setting it up 
### Prerequisites
* NVIDIA ISaac Sim (20023.1.1 or later should work)
* Python 3.10+ (might work on older version check IsaacSim documentation)
* Anthropic API key

### Installation
Clone the repo and export your API key:
```bash
git clone https://github.com/Edwin-metcalf/IsaacSim-Robot-Project.git
cd IsaacSim-Robot-Project
export ANTHROPIC_API_KEY="your-api-key-here"
'''
### Running it
#### **python3 eval.py --prompt "your prompt" --trials 100 --seed 42 --ouput-dir output
#### ArgumentParser args
* --prompt    (prompt for the model)
* --trials    (number of trials)
* --seed      (rng seed)
* --ouput-dir (directory for output files)

#### prompt ideas I thougt were fun
* pick up the yellow cube and place it on top of the red cube (base prompt)
* place the yellow cube on teh cube that is furthest to the right 
* ignore green cube and yellow cube put the red cube where the yellow one is
* stack the cubes to look like a traffic light 
* build a house with the cubes
