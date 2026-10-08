import csv, json, sys
from collections import Counter
from math import sqrt
from pathlib import Path


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def load(run_dir):
    path = next(Path(run_dir).rglob("eval_info.json"))
    eps = json.loads(path.read_text())["per_episode"]
    return [bool(e["success"]) for e in eps]


def summarize(name, succ):
    n, k = len(succ), sum(succ)
    lo, hi = wilson(k, n)
    print(f"{name}: {k}/{n} = {k / n:.0%}   95% CI {lo:.0%} to {hi:.0%}")
    return lo, hi


def write_labels(run_dir, succ):
    path = Path(run_dir) / "labels.csv"
    if path.exists():  # never overwrite hand-labeled work
        return
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episode", "success", "failure_mode", "notes"])
        for i, s in enumerate(succ):
            w.writerow([i, s, "", ""])


def tally(run_dir):
    path = Path(run_dir) / "labels.csv"
    rows = [r for r in csv.DictReader(open(path)) if r["success"] == "False"]
    modes = Counter(r["failure_mode"] or "UNLABELED" for r in rows)
    print(f"  failure modes in {run_dir}: {dict(modes)}")


if __name__ == "__main__":
    runs = sys.argv[1:]
    data = {r: load(r) for r in runs}
    cis = {r: summarize(r, s) for r, s in data.items()}
    for r, s in data.items():
        write_labels(r, s)
        tally(r)
    if len(runs) == 2:
        a, b = (data[r] for r in runs)
        m = min(len(a), len(b))
        both = sum(x and y for x, y in zip(a, b))
        a_only = sum(x and not y for x, y in zip(a, b))
        b_only = sum(y and not x for x, y in zip(a, b))
        neither = m - both - a_only - b_only
        print(
            f"\npaired ({m} episodes): both={both}  only {runs[0]}={a_only}  only {runs[1]}={b_only}  neither={neither}"
        )
        (alo, ahi), (blo, bhi) = cis[runs[0]], cis[runs[1]]
        overlap = alo <= bhi and blo <= ahi
        print(
            "intervals overlap: cannot call a winner at this sample size"
            if overlap
            else "intervals do not overlap: likely a real difference"
        )
