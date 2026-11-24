#!/usr/bin/env python3
"""Randomly choose Frutiger Aero motifs from references/motifs.json.

Usage: python3 pick_motifs.py [--tier 1|2|3] [--seed N] [--theme "domain words"] [--json]
Picks per category are random within the min/max in the catalogue; categories
marked required always get at least one. Tier caps the motif complexity (a motif
with tier > --tier is skipped). Prints the seed so a run can be reproduced.
"""
import argparse, json, os, random, sys

p = argparse.ArgumentParser()
p.add_argument("--tier", type=int, default=3)
p.add_argument("--seed", type=int)
p.add_argument("--theme", default="")
p.add_argument("--json", action="store_true")
a = p.parse_args()

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "motifs.json")
data = json.load(open(path))
seed = a.seed if a.seed is not None else random.SystemRandom().randrange(10**6)
rng = random.Random(seed)
words = {w.lower() for w in a.theme.replace(",", " ").split() if len(w) > 2}

picks = []
for cat, cfg in data["categories"].items():
    pool = [m for m in data["motifs"] if m["cat"] == cat and m["tier"] <= a.tier]
    if not pool:
        continue
    lo, hi = cfg["pick"]
    n = rng.randint(lo, hi)
    if cfg["required"]:
        n = max(n, 1)
    # theme words nudge selection: motifs whose text mentions a theme word get double weight
    weights = [2 if words & set((m["name"] + " " + m["how"]).lower().split()) else 1 for m in pool]
    chosen = []
    pool = pool[:]
    while pool and len(chosen) < n:
        m = rng.choices(pool, weights=weights)[0]
        i = pool.index(m)
        pool.pop(i); weights.pop(i)
        chosen.append(m)
    picks += chosen

if a.json:
    json.dump({"seed": seed, "tier": a.tier, "picks": picks}, sys.stdout, indent=1)
else:
    print(f"seed={seed} tier<={a.tier} total={len(picks)}")
    for cat, cfg in data["categories"].items():
        rows = [m for m in picks if m["cat"] == cat]
        if rows:
            print(f"\n[{cfg['label']}]")
            for m in rows:
                print(f"  - {m['id']}: {m['name']} (T{m['tier']}) -- {m['how']}")
