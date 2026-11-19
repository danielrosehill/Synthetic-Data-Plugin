# /// script
# requires-python = ">=3.10"
# ///
"""Draw seeded combinations from an axes file (step 1 of seed-then-write).

axes.json: {"who": ["a", "b"], "tone": ["x", "y"], ...}
Usage: uv run axes.py axes.json --n 200 --seed 1 > combos.jsonl
Each line: {"i": 0, "who": ..., "tone": ...}. Combinations are drawn without
repeats until the space is exhausted, then with repeats.
"""
import argparse, itertools, json, random, sys

p = argparse.ArgumentParser()
p.add_argument("axes"); p.add_argument("--n", type=int, required=True); p.add_argument("--seed", type=int, default=0)
a = p.parse_args()
axes = json.load(open(a.axes))
rng = random.Random(a.seed)
size = 1
for v in axes.values():
    size *= len(v)
if size <= 200_000:
    space = list(itertools.product(*axes.values())); rng.shuffle(space)
    combos = [space[i % len(space)] for i in range(a.n)]
else:
    seen, combos = set(), []
    while len(combos) < a.n:
        c = tuple(rng.choice(v) for v in axes.values())
        if c in seen and len(seen) < size: continue
        seen.add(c); combos.append(c)
for i, c in enumerate(combos):
    print(json.dumps({"i": i, **dict(zip(axes.keys(), c))}, ensure_ascii=False))
