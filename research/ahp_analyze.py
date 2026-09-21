"""Turn AHP survey responses into factor weights - with the honesty checks.

    python research/ahp_analyze.py                  # uses ahp_responses.csv
    python research/ahp_analyze.py --demo           # synthetic data, to test the pipeline

It writes reports/ahp_weights.json and never edits the engine: a person reviews
the weights and copies them into PROFILES in engine/factors.py.

WHAT THIS DOES
--------------
1. Builds each respondent's pairwise comparison matrix, one row and column per
   factor in engine/factors.py (4x4 today).
2. Derives their priority vector by the ROW GEOMETRIC MEAN method. (The principal
   eigenvector gives near-identical answers and is harder to defend in a viva.)
3. Computes the Consistency Ratio and DROPS anyone above 0.10. Reports how many.
4. Aggregates survivors by geometric mean of their JUDGEMENTS (AIJ), the standard
   for a consensus panel, then derives group priorities from that.
5. Reports the SPREAD across respondents - the disagreement is a finding, not noise.
6. Bootstraps respondents 1000x to give a per-stock top-10 stability figure,
   re-ranking today's stocks on the factor_z values engine/run_today.py publishes.

WHY THE BOOTSTRAP MATTERS
-------------------------
Most sensitivity analyses say "we varied the weights by +/-10%", and the first
question is: why 10%? There is no answer. Instead we resample the actual experts,
so the perturbation range IS the measured disagreement among them. That turns
"how confident are you?" into something we can answer with data we collected:

    "PTT appears in the top 10 under 87% of expert weightings."

That is a defensible confidence number, and it is the intended replacement for
the p_win figure the app used to invent.

INPUT FORMAT  (research/ahp_responses.csv)
    respondent,profile,left,right,winner,strength
    E01,conservative,momentum,roe,roe,3
    ...
    winner must be one of left / right / "equal"; strength 1-9 (1 when equal)
"""
import csv
import itertools
import json
import os
import sys

import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))
from factors import FACTORS                     # single source of truth (engine/factors.py)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(HERE, "research")
REPORTS = os.path.join(HERE, "reports")
TODAY = os.path.join(HERE, "engine", "today.json")
DRAWS = 1000                                   # bootstrap resamples of the panel
TOP = 10
N = len(FACTORS)
RI = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32}   # Saaty random index
CR_LIMIT = 0.10
PROFILES = ["conservative", "balanced", "aggressive"]


# ---------------------------------------------------------------- core AHP
def matrix_from(rows):
    """rows: list of (left, right, winner, strength) -> N x N comparison matrix."""
    A = np.ones((N, N))
    for left, right, winner, strength in rows:
        i, j = FACTORS.index(left), FACTORS.index(right)
        s = float(strength)
        if winner == "equal" or s <= 1:
            v = 1.0
        elif winner == left:
            v = s
        elif winner == right:
            v = 1.0 / s
        else:
            raise ValueError(f"winner {winner!r} is neither {left!r} nor {right!r}")
        A[i, j], A[j, i] = v, 1.0 / v
    return A


def priorities(A):
    """Row geometric mean, normalised."""
    g = np.prod(A, axis=1) ** (1.0 / N)
    return g / g.sum()


def consistency_ratio(A, w):
    """CR = CI/RI. Below 0.10 is conventionally acceptable."""
    lam = float(np.mean((A @ w) / w))
    ci = (lam - N) / (N - 1)
    return ci / RI[N], lam


# ---------------------------------------------------------------- input
def load(path):
    """-> {profile: {respondent: [(left, right, winner, strength), ...]}}"""
    out = {p: {} for p in PROFILES}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            p = r["profile"].strip().lower()
            if p not in out:
                continue
            out[p].setdefault(r["respondent"].strip(), []).append(
                (r["left"].strip().lower(), r["right"].strip().lower(),
                 r["winner"].strip().lower(), r["strength"].strip()))
    return out


def synthetic(n=8, seed=11):
    """Plausible fake panel, so the pipeline can be tested before real data lands."""
    rng = np.random.default_rng(seed)
    truth = {
        "conservative": {"quality": 5, "health": 4, "momentum": 1, "roe": 1},
        "balanced":     {"quality": 3, "momentum": 2, "health": 2, "roe": 2},
        "aggressive":   {"momentum": 5, "roe": 4, "quality": 1, "health": 1},
    }
    out = {p: {} for p in PROFILES}
    for p in PROFILES:
        for k in range(n):
            rid = f"E{k + 1:02d}"
            rows = []
            for a, b in itertools.combinations(FACTORS, 2):
                ratio = truth[p][a] / truth[p][b] * float(rng.normal(1.0, 0.28))
                ratio = min(max(ratio, 1 / 9), 9)
                if 0.9 < ratio < 1.15:
                    rows.append((a, b, "equal", 1))
                elif ratio > 1:
                    rows.append((a, b, a, int(round(min(9, max(2, ratio))))))
                else:
                    rows.append((a, b, b, int(round(min(9, max(2, 1 / ratio))))))
            out[p][rid] = rows
    return out


# ---------------------------------------------------------------- reporting
def analyse(data):
    results, dropped_all = {}, {}
    for p in PROFILES:
        kept, dropped, crs = {}, [], []
        for rid, rows in data[p].items():
            if len(rows) < N * (N - 1) // 2:
                dropped.append((rid, f"incomplete ({len(rows)}/{N * (N - 1) // 2} pairs)"))
                continue
            A = matrix_from(rows)
            w = priorities(A)
            cr, _ = consistency_ratio(A, w)
            crs.append(cr)
            if cr < CR_LIMIT:
                kept[rid] = (A, w, cr)
            else:
                dropped.append((rid, f"CR {cr:.3f} >= {CR_LIMIT}"))
        results[p] = (kept, crs)
        dropped_all[p] = dropped
    return results, dropped_all


def group_weights(kept):
    """AIJ: geometric mean of the judgement matrices, then derive priorities."""
    mats = np.array([A for A, _, _ in kept.values()])
    return priorities(np.exp(np.mean(np.log(mats), axis=0)))


def bootstrap(kept, factor_z, draws=DRAWS, top=TOP, seed=11):
    """How often each stock makes the top `top` when the panel is resampled.

    Each draw picks len(kept) respondents with replacement, aggregates them the
    same way as the headline weights (AIJ), scores today's stocks with those
    weights and records the top `top`. The spread therefore comes from the
    experts' real disagreement, not from an arbitrary +/-10%.
    Returns {ticker: share of draws}, most stable first.
    """
    rng = np.random.default_rng(seed)
    mats = np.array([A for A, _, _ in kept.values()])
    tickers = list(factor_z)
    Z = np.array([[factor_z[t][f] for f in FACTORS] for t in tickers])
    counts = np.zeros(len(tickers))
    for _ in range(draws):
        pick = rng.integers(0, len(mats), size=len(mats))
        w = priorities(np.exp(np.mean(np.log(mats[pick]), axis=0)))
        counts[np.argsort(-(Z @ w), kind="stable")[:top]] += 1
    order = np.argsort(-counts, kind="stable")
    return {tickers[i]: float(counts[i] / draws) for i in order if counts[i] > 0}


def main():
    demo = "--demo" in sys.argv
    path = os.path.join(RESEARCH, "ahp_responses.csv")
    if demo:
        print("*** DEMO MODE - synthetic responses, NOT real survey data ***\n")
        data = synthetic()
    elif os.path.exists(path):
        data = load(path)
    else:
        print(f"No responses yet at research/ahp_responses.csv")
        print("Run with --demo to exercise the pipeline on synthetic data.")
        return 1

    results, dropped = analyse(data)

    print(f"{'profile':<14}{'responded':>10}{'kept':>7}{'dropped':>9}{'mean CR':>9}")
    for p in PROFILES:
        kept, crs = results[p]
        print(f"{p:<14}{len(data[p]):>10}{len(kept):>7}{len(dropped[p]):>9}"
              f"{np.mean(crs) if crs else float('nan'):>9.3f}")
    for p in PROFILES:
        for rid, why in dropped[p]:
            print(f"  dropped {p}/{rid}: {why}")

    print(f"\n{'=' * 74}\nGROUP WEIGHTS (geometric mean of judgements, inconsistent responses removed)")
    print(f"{'=' * 74}")
    print(f"{'profile':<14}" + "".join(f"{f:>11}" for f in FACTORS))
    final = {}
    for p in PROFILES:
        kept, _ = results[p]
        if not kept:
            print(f"{p:<14}  no usable responses")
            continue
        w = group_weights(kept)
        final[p] = {f: round(float(x), 3) for f, x in zip(FACTORS, w)}
        print(f"{p:<14}" + "".join(f"{x * 100:>10.1f}%" for x in w))

    print(f"\nSPREAD ACROSS RESPONDENTS (min-max) - this disagreement IS the")
    print(f"perturbation range for sensitivity, instead of an arbitrary +/-10%")
    for p in PROFILES:
        kept, _ = results[p]
        if len(kept) < 2:
            continue
        W = np.array([w for _, w, _ in kept.values()])
        print(f"  {p:<14}" + "  ".join(
            f"{f[:4]} {W[:, i].min() * 100:.0f}-{W[:, i].max() * 100:.0f}%"
            for i, f in enumerate(FACTORS)))

    stability = {}
    factor_z = json.load(open(TODAY, encoding="utf-8")).get("factor_z") if os.path.exists(TODAY) else None
    if not factor_z:
        print("\n(no factor_z in engine/today.json - run engine/run_today.py first; bootstrap skipped)")
    else:
        print(f"\nTOP-{TOP} STABILITY - {DRAWS} resamples of the panel, on today's factor values")
        print(f"share of resamples in which each stock stays in the top {TOP}")
        for p in PROFILES:
            kept, _ = results[p]
            if len(kept) < 2:
                continue
            freq = bootstrap(kept, factor_z)
            stability[p] = {t: round(v, 3) for t, v in freq.items()}
            shown = ", ".join(f"{t.replace('.BK', '')} {v:.0%}" for t, v in list(freq.items())[:12])
            print(f"  {p:<14}{shown}")

    if final:
        os.makedirs(REPORTS, exist_ok=True)
        out = os.path.join(REPORTS, "ahp_weights.json")
        json.dump({"weights": final, "demo": demo, "top10_stability": stability,
                   "stability_draws": DRAWS,
                   "kept": {p: len(results[p][0]) for p in PROFILES},
                   "dropped": {p: len(dropped[p]) for p in PROFILES}},
                  open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"\n-> wrote reports/ahp_weights.json")
        if demo:
            print("   (demo data - do NOT paste these into engine/factors.py)")
        else:
            print("   Review, then copy into PROFILES in engine/factors.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
