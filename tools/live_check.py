"""Live check - is the public site running the engine this repo describes?

    python tools/live_check.py                 # checks https://setscout-th.web.app/today.json
    python tools/live_check.py <url-or-file>   # any today.json

WHY THIS EXISTS
---------------
On 3 Oct 2026 the live site was found serving a fresh today.json (dated the day
before) produced by an engine two weeks old: it still weighted "growth", still
emitted p_win on every stock and had no ROE. The daily job was healthy, so the
freshness monitor was green. Nothing compared WHAT the live engine computes with
what engine/factors.py says it computes.

This is the "built, documented, never wired in" failure again (the tally is in
docs/CONTINUE.md): the change was merged nowhere the live site reads from.

It compares the live file with the code in this checkout:
  1. the factor set under every profile     == factors.FACTORS
  2. every profile's weights                == factors.PROFILES
  3. no stock carries a retired field       (p_win)
  4. per-factor scores (factor_z) are there, for the same factors
  5. every stock in the universe was scored
  6. the file is recent                      (<= MAX_AGE_DAYS old)

Exit code 0 when all agree, 1 with one line per difference. It needs the network,
so it is NOT part of the pull-request checks: run it by hand after a deploy, or
on a schedule.
"""
import datetime
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "engine"))
from factors import FACTORS, PROFILES            # single source of truth - do not copy

LIVE = "https://setscout-th.web.app/today.json"
RETIRED_FIELDS = ["p_win"]                        # removed from the product on 2026-09-16
MAX_AGE_DAYS = 4                                  # a long weekend, not a stalled job


def fetch(src):
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    return json.load(open(src, encoding="utf-8"))


def compare(d, today=None):
    """Return the list of differences between a today.json and this checkout."""
    out = []
    weights = d.get("profile_weights") or {}
    for name, want in PROFILES.items():
        got = weights.get(name)
        if got is None:
            out.append(f"profile '{name}' is missing from profile_weights")
            continue
        if set(got) != set(FACTORS):
            out.append(f"{name}: live factors {sorted(got)} != code {sorted(FACTORS)}")
        elif any(abs(got[f] - want[f]) > 1e-6 for f in FACTORS):
            out.append(f"{name}: live weights {got} != code {want}")
    stocks = d.get("stocks") or []
    for field in RETIRED_FIELDS:
        n = sum(field in s for s in stocks)
        if n:
            out.append(f"{n} of {len(stocks)} stocks still carry the retired field '{field}'")
    fz = d.get("factor_z")
    if not fz:
        out.append("factor_z is missing (the AHP stability figure cannot be computed from this file)")
    else:
        seen = set(next(iter(fz.values())))
        if seen != set(FACTORS):
            out.append(f"factor_z has {sorted(seen)}, code has {sorted(FACTORS)}")
    if d.get("scored") != d.get("universe_size"):
        out.append(f"scored {d.get('scored')} of {d.get('universe_size')} stocks")
    try:
        age = ((today or datetime.date.today()) - datetime.date.fromisoformat(d["generated"])).days
        if age > MAX_AGE_DAYS:
            out.append(f"generated {d['generated']}, {age} days ago (limit {MAX_AGE_DAYS})")
    except (KeyError, ValueError):
        out.append(f"generated date unreadable: {d.get('generated')!r}")
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else LIVE
    try:
        d = fetch(src)
    except Exception as e:                        # network or parse failure is a failed check
        print(f"FAIL could not read {src}: {e}")
        return 1
    diffs = compare(d)
    print(f"{src}\n  generated {d.get('generated')}, code factors {FACTORS}")
    if not diffs:
        print("OK  the live file matches the engine in this checkout.")
        return 0
    for line in diffs:
        print(f"FAIL {line}")
    print(f"{len(diffs)} difference(s): the live site is not running this engine.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
