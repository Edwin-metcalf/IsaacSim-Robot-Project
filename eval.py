import argparse
import sys

def str2bool(v):
    #helpeer funciton to convert user string into a bool
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    parser = argparse.ArgumentParser(description="Evaluate VLM-driven pick and place in Isaac Sim.")
    parser.add_argument("--prompt", type=str, default="pick up the yellow cube and place it on top of the red cube",
                        help="The natural language instruction for the VLM.")
    parser.add_argument("--trials", type=int, default=5,
                        help="Number of evaluation trials to run.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for cube placement.")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Directory to save the JSON results.")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="Enable verbose output for debugging.")
    
    args = parser.parse_args()

    print(f"Starting Evaluation with {args.trials} trials...")
    print(f"Task Prompt: '{args.prompt}'")

    from isaacsim import SimulationApp
    app = SimulationApp({'headless': True})

    from test_vlm import run_evaluation

    try:
        run_evaluation(
            TASK_PROMPT=args.prompt,
            NUM_TRIALS=args.trials,
            seed=args.seed,
            output_dir=args.output_dir,
            verbose=args.verbose
            )
    except Exception as e:
        print(f"Evaluation failed: {e}")
    finally:
        app.close()


if __name__ == "__main__":
    main()


