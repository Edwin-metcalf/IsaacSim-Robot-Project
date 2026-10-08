#!/usr/bin/env python3
"""usage: python compare.py runs/<A> runs/<B> [runs/<C> ...]
Runs must use the same seed, n_episodes and batch_size to be a valid pairing."""
import ast, math, sys
from math import comb
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

def tag(ok, mr):
    if ok: return "OK"
    return "near" if mr >= 0.9 else "part" if mr >= 0.5 else "none"

def mcnemar(b, c):  # exact two-sided sign test on discordant pairs
    n = b + c
    if n == 0: return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)

runs = sys.argv[1:]
if len(runs) < 2: sys.exit(__doc__)
names = [Path(r).name for r in runs]
data = [load(r) for r in runs]
ns = {len(d["successes"]) for d in data}
if len(ns) != 1: sys.exit(f"episode counts differ: {sorted(ns)}; cannot pair")
n = ns.pop()

w = max(12, *(len(x) for x in names)) + 2
bar = "-" * (5 + w * len(runs))
print(f"\n{bar}\n{'ep':>3}  " + "".join(f"{x:<{w}}" for x in names) + f"\n{bar}")
for i in range(n):
    cells = [f"{tag(d['successes'][i], d['max_rewards'][i])} {d['max_rewards'][i]:.3f}" for d in data]
    print(f"{i:>3}  " + "".join(f"{c:<{w}}" for c in cells))
print(bar)
for name, d in zip(names, data):
    k = sum(d["successes"]); lo, hi = wilson(k, n)
    print(f"{name:<{w}}{k}/{n} = {100*k/n:5.1f}%   Wilson 95% CI {lo:.1f}% to {hi:.1f}%   mean max_r {sum(d['max_rewards'])/n:.3f}")
print(bar)
a = data[0]["successes"]
for name, d in zip(names[1:], data[1:]):
    s = d["successes"]
    both = sum(x and y for x, y in zip(a, s)); only_a = sum(x and not y for x, y in zip(a, s))
    only_b = sum(y and not x for x, y in zip(a, s)); neither = n - both - only_a - only_b
    print(f"{names[0]} vs {name}: both {both} | only {names[0]} {only_a} | only {name} {only_b} | neither {neither} | exact McNemar p = {mcnemar(only_a, only_b):.3f}")
print()
