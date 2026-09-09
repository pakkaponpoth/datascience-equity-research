"""Health check for the daily refresh - fails LOUDLY when today.json is bad.

    python verify_today.py          # exit 0 = healthy, exit 1 = broken

Run by .github/workflows/refresh-setscout.yml immediately after run_today.py and
BEFORE the commit step. Why it exists: the workflow's commit step is
`git diff --staged --quiet || git commit`, so a crashed engine committed nothing
and report nothing - a silent failure path with no alarm on it. A non-zero exit
here fails the job, which GitHub emails about.

(An earlier version of this docstring claimed the Action had been dead 9-30 Aug.
That was wrong: it ran every day, 22 commits. The diagnosis came from a local git
log that had never been fetched. This guard closes a real hole, but a hypothetical
one - not an observed outage.)

No third-party dependencies on purpose - this must still run when the engine's
own dependencies are what broke.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_COVERAGE = 0.90          # at least this share of the universe must score


def _load(name):
    return json.load(open(os.path.join(HERE, name), encoding="utf-8"))


def main():
    problems = []

    try:
        d = _load("today.json")
    except (OSError, ValueError) as e:
        print(f"FATAL: cannot read today.json - {e}")
        return 1

    try:
        expected = len(_load("universe.json")["stocks"])
    except (OSError, KeyError, ValueError):
        expected = None
        problems.append("universe.json missing or unreadable - the engine had no canonical list")

    stocks = d.get("stocks") or []
    n = len(stocks)
    if expected and n < expected * MIN_COVERAGE:
        problems.append(f"only {n}/{expected} stocks scored "
                        f"({n / expected:.0%}, need {MIN_COVERAGE:.0%})")
    elif n < 50:
        problems.append(f"only {n} stocks scored")

    today = datetime.date.today().isoformat()
    if d.get("generated") != today:
        problems.append(f"generated={d.get('generated')!r} but today is {today} "
                        "- the engine did not actually rewrite the file")

    profiles = d.get("profiles") or {}
    for name in ("conservative", "balanced", "aggressive"):
        if name not in profiles:
            problems.append(f"profile {name!r} is missing")
        elif len(profiles[name]) != n:
            problems.append(f"profile {name!r} has {len(profiles[name])} rows, expected {n}")

    if d.get("calibration") is None:
        problems.append("calibration is null - p_win would render blank; run backtest.py")

    no_price = [s.get("ticker") for s in stocks if not s.get("last")]
    if no_price:
        problems.append(f"{len(no_price)} stock(s) have no price, e.g. {no_price[:5]}")

    if problems:
        print("REFRESH FAILED ITS HEALTH CHECK - nothing should be committed")
        for p in problems:
            print(f"  - {p}")
        print("\nMost likely cause: Yahoo Finance rate-limiting the GitHub runner.")
        print("Re-run from the Actions tab, or run the engine locally and commit that.")
        return 1

    cal = d.get("calibration") or {}
    print(f"OK - {n} stocks scored, generated {d.get('generated')}, "
          f"calibration measured {cal.get('generated')} over {cal.get('months')} months "
          f"(base rate {cal.get('base_rate')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
