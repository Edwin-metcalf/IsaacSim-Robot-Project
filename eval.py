import argparse
import sys

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
            output_dir=args.output_dir
            )
    except Exception as e:
        print(f"Evaluation failed: {e}")
    finally:
        app.close()


if __name__ == "__main__":
    main()


