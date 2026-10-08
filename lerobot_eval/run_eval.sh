#!/usr/bin/env bash
# usage: ./run_eval.sh <run_name> <policy_path> <n_episodes> <seed>
set -euo pipefail
name=$1
policy=$2
n=$3
seed=$4
out=runs/$name
mkdir -p "$out"
lerobot-eval \
  --policy.path="$policy" --env.type=pusht \
  --eval.n_episodes="$n" --eval.batch_size=10 \
  --seed="$seed" --output_dir="$out" --policy.device=cuda \
  2>&1 | tee "$out/log.txt"
echo "policy=$policy n=$n seed=$seed date=$(date -Is)" >"$out/meta.txt"
