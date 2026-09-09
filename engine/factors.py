"""Single source of truth for the factor set and the profile weights.

WHY THIS FILE EXISTS
--------------------
Until 2026-09-09 this definition was copy-pasted into ten files: run_today.py,
ahp_analyze.py, and eight scripts in research/. Several carried the comment
"# FROZEN - identical to run_today.py". None of them were kept in step.

When "value" was removed from the engine, every one of those copies kept
scoring the old five-factor model, so every report in reports/ described
software that no longer shipped. profiles_demo.py had drifted even earlier -
its balanced weights (.25/.25/.20/.15/.15) never matched the engine at all.

That is the third instance of one failure mode in this project:

  1. calibration.json was measured, documented, and never wired into run_today
  2. ahp_analyze.py's docstring promises a bootstrap that was never written
  3. this - a value defined in one place, copied, and left to drift

Import from here. Do not copy.

FROZEN SNAPSHOTS
----------------
Pre-registered tests must NOT follow the live weights - re-running a one-shot
test after changing the model is the p-hacking the design exists to prevent.
They import a dated snapshot from FROZEN instead, which makes the freeze
deliberate and auditable rather than an accident of copy-paste.
"""

# ---------------------------------------------------------------- live
FACTORS = ["momentum", "growth", "quality", "health"]

# "value" was removed 2026-09-09. Computed as price vs its own 200-day average,
# it correlated -0.93 with momentum across the universe (86% shared variance,
# beta -1.00 on z-scores) - momentum with the sign flipped, not a fifth
# dimension. Weighting both meant they cancelled, and because value carried the
# larger weight in "balanced" (.24 vs .20) it won the remainder, which is why
# balanced shared 8 of its top 10 names with conservative.
#
# It was also misnamed: this measured mean reversion. Real value needs an
# external anchor (earnings, book value) that a price-only engine does not have.
PROFILES = {
    "conservative": {"quality": .50, "health": .38, "momentum": .06, "growth": .06},
    "balanced":     {"quality": .37, "momentum": .26, "health": .21, "growth": .16},
    "aggressive":   {"momentum": .47, "growth": .35, "quality": .12, "health": .06},
}

# ------------------------------------------------------------- frozen
FROZEN = {
    "2026-08-31": {
        "factors": ["momentum", "growth", "value", "quality", "health"],
        "profiles": {
            "conservative": {"quality": .40, "health": .30, "value": .20,
                             "momentum": .05, "growth": .05},
            "balanced":     {"quality": .28, "value": .24, "momentum": .20,
                             "health": .16, "growth": .12},
            "aggressive":   {"momentum": .40, "growth": .30, "value": .15,
                             "quality": .10, "health": .05},
        },
        "used_by": ["blind_test.py", "backtest_sizing.py"],
        "why": "The weights these pre-registered one-shots were actually run "
               "against. Do not update them to match the live engine - that "
               "would silently re-run a sealed test on a changed model.",
    },
}


def check(factors=None, profiles=None):
    """Fail loudly if the weights stop being a valid weight set.

    Called at import. A profile whose weights do not sum to 1, or whose keys
    do not match the factor list, is a bug that would otherwise show up as a
    quietly wrong ranking.
    """
    factors = FACTORS if factors is None else factors
    profiles = PROFILES if profiles is None else profiles
    for name, w in profiles.items():
        if set(w) != set(factors):
            raise ValueError(
                f"{name}: weights {sorted(w)} do not match factors {sorted(factors)}")
        total = sum(w.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"{name}: weights sum to {total:.4f}, expected 1.0")
    return True


check()
for _tag, _snap in FROZEN.items():
    check(_snap["factors"], _snap["profiles"])
