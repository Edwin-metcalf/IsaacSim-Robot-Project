#!/usr/bin/env python3
"""usage: python summarize.py runs/<name>"""
import ast, math, sys
from collections import Counter
from pathlib import Path

def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)

def load(run):
    for line in Path(run, "log.txt").read_text().splitlines():
        if "'sum_rewards'" in line:
            return ast.literal_eval(line[line.index("[{"):])[0]["metrics"]
    sys.exit(f"no per-task metrics found in {run}/log.txt")

def category(ok, mr):
    if ok: return "success"
    if mr >= 0.9: return "near miss"
    if mr >= 0.5: return "partial"
    return "no progress"

run = sys.argv[1]
m = load(run)
rows = list(zip(m["successes"], m["max_rewards"], m["sum_rewards"]))
cats = [category(ok, mr) for ok, mr, _ in rows]
bar = "-" * 34
print(f"\n{run}\n{bar}\n{'ep':>3}  {'result':<12}{'max_r':>6}{'sum_r':>9}\n{bar}")
for i, ((ok, mr, sr), c) in enumerate(zip(rows, cats)):
    print(f"{i:>3}  {c:<12}{mr:>6.3f}{sr:>9.1f}")
n, k = len(rows), sum(r[0] for r in rows)
lo, hi = wilson(k, n)
print(bar)
print(f"success {k}/{n} = {100*k/n:.1f}%   Wilson 95% CI {lo:.1f}% to {hi:.1f}%")
print("outcomes: " + ", ".join(f"{c} x{v}" for c, v in Counter(cats).most_common()))
print(f"mean max_r {sum(r[1] for r in rows)/n:.3f}   mean sum_r {sum(r[2] for r in rows)/n:.1f}\n")
