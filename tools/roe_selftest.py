"""ROE quality gate - fault injection self-test.

    python tools/roe_selftest.py

WHY THIS EXISTS
---------------
engine/roe_data.py withholds ROE values it judges to be extraction failures
rather than business facts. That judgement is a rule someone wrote, and a rule
that has never been tested against data it could fail on is a rule nobody should
trust with what the site publishes.

So this test manufactures its own ground truth. It takes rows the gate currently
ACCEPTS, breaks them with exactly the faults found in the real data, and asks two
questions with checkable answers:

    DETECTION   of the rows broken on purpose, how many does the gate catch -
                and how many untouched rows does it wrongly flag? A detector
                that flags everything scores 100% on the first and is useless.

    RECOVERY    of the rows it catches, how many can be restored to the value
                they had before being broken? We know that value, because we
                are the ones who broke it.

The four faults are the ones actually observed on 2026-09-20:

    equity read 1000x too large      SCB 2012 carried equity of 154 trillion baht
    profit scaled by 1e-6            AOT 2005 became 0.0001%, from the parser's
                                     own "inferred rescale" when a ratio exceeded 1
    a year repeated verbatim         MEGA carried 14.2436% for 2015, 2016 and 2017
    a value driven to zero           KTB read 0.0000% for four straight years

A recovery that is close but not exact is worse than no recovery, because it
publishes a plausible wrong number under a company's name. So the repair is
required to refuse unless the corrected figure also agrees with that company's
own neighbouring years, and the test counts refusals separately from errors.

Standard library only, so CI needs no installs.
"""
import csv
import os
import pathlib
import random
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE))
import roe_data as rd  # noqa: E402

SAMPLE = 200
SEED = 11                    # fixed, so a failure can be reproduced exactly
MAX_RATIO = 0.60
DETECTION_FLOOR = 0.95       # below this, the gate is not doing its job
FALSE_POSITIVE_CEILING = 0.01


def load():
    by = defaultdict(list)
    with open(ENGINE / "roe_history.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            by[r["ticker"]].append((int(r["fiscal_year"]), float(r["roe"])))
    for t in by:
        by[t].sort()
    return by


def gate_flags(series, i):
    """Ask the SHIPPED gate about one series - not a copy of its logic."""
    return rd._suspect([(None, v, y) for y, v in series], i)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(SEED)
    by = load()
    already = {(t, y) for t, y, _v in rd.flagged()}

    candidates = [(t, i, y, v)
                  for t, series in by.items()
                  for i, (y, v) in enumerate(series)
                  if (t, y) not in already and v and 0 < i < len(series) - 1
                  and abs(v) > 0.02]
    if len(candidates) < SAMPLE:
        print(f"only {len(candidates)} clean rows available - need {SAMPLE}")
        return 1
    picked = random.sample(candidates, SAMPLE)
    print(f"ROE gate self-test - {SAMPLE} clean rows, seed {SEED}\n")

    faults = {
        "equity read 1000x too large": lambda v, prev: v / 1000.0,
        "profit scaled by 1e-6": lambda v, prev: v * 1e-6,
        "year repeated verbatim": lambda v, prev: prev,
        "value driven to zero": lambda v, prev: 0.0,
    }

    print(f"  {'fault injected':<30}{'caught':>8}{'missed':>8}{'rate':>9}")
    worst = 1.0
    for name, fn in faults.items():
        caught = 0
        for t, i, y, v in picked:
            series = list(by[t])
            series[i] = (y, fn(v, series[i - 1][1]))
            caught += gate_flags(series, i)
        rate = caught / SAMPLE
        worst = min(worst, rate)
        print(f"  {name:<30}{caught:>8}{SAMPLE - caught:>8}{rate * 100:>8.1f}%")

    fp = clean = 0
    for t, series in by.items():
        for i, (y, _v) in enumerate(series):
            if (t, y) in already:
                continue
            clean += 1
            fp += gate_flags(series, i)
    fp_rate = fp / clean if clean else 0
    print(f"\n  false positives on untouched rows   {fp} of {clean:,} "
          f"({fp_rate * 100:.2f}%)")

    # ---- recovery ----
    recovered = refused = wrong = undetected = 0
    for t, i, y, v in picked:
        series = list(by[t])
        series[i] = (y, v / 1000.0)
        if not gate_flags(series, i):
            undetected += 1
            continue
        neigh = [abs(x) for j, (_yy, x) in enumerate(series)
                 if j != i and abs(i - j) <= 2 and x]
        med = sorted(neigh)[len(neigh) // 2] if neigh else None
        best = None
        for p in (1e3, 1e-3, 1e6, 1e-6):
            cand = series[i][1] * p
            if abs(cand) > MAX_RATIO:
                continue
            if med and not (0.5 <= abs(cand) / med <= 2.0):
                continue
            best = cand
            break
        if best is None:
            refused += 1
        elif abs(best - v) < 1e-9:
            recovered += 1
        else:
            wrong += 1

    tested = SAMPLE - undetected
    print(f"\n  recovery, on the fault the repair is built for")
    print(f"    caught and attempted              {tested}")
    print(f"    restored to the exact value       {recovered} "
          f"({recovered / tested * 100:.1f}%)" if tested else "")
    print(f"    declined, row stays withheld      {refused}")
    print(f"    restored to a WRONG value         {wrong}   <- must be zero")

    ok = worst >= DETECTION_FLOOR and fp_rate <= FALSE_POSITIVE_CEILING and wrong == 0
    print(f"\n  detection floor {DETECTION_FLOOR * 100:.0f}%: worst was {worst * 100:.1f}%")
    print(f"  false-positive ceiling {FALSE_POSITIVE_CEILING * 100:.0f}%: was {fp_rate * 100:.2f}%")
    print(f"  wrong repairs must be 0: was {wrong}")
    print("\n" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
