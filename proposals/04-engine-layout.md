# Proposal 04: should `engine/` be split up?

*Status: proposal, 3 Oct 2026. Nothing has been moved. This needs a team decision.*

## The problem

`engine/` holds 19 files that do three different jobs:

| Job | Files | Count |
|---|---|---|
| **Daily line**: runs every day, produces `today.json` | `run_today.py`, `factors.py`, `roe_data.py`, `verify_today.py`, `universe.json`, `roe_history.csv`, `today.json` | 7 |
| **Test bench**: backtests and explorers, re-runnable | `backtest.py`, `backtest_hold.py`, `backtest_long.py`, `backtest_costs.py`, `backtest_profiles.py`, `profiles_demo.py`, `explore.py`, `rederive_section34.py`, `reportlib.py`, `paths.py` | 10 |
| **Sealed vault**: pre-registered one-shots, never re-run | `blind_test.py`, `backtest_sizing.py` | 2 |

A newcomer opening the folder can't tell which seven files are the product and which twelve are the evidence.

## What is already done (no files moved)

The codebase map now draws `engine/` as these three zones. The folder on disk is unchanged. If the only goal is to make the engine easier to read, that may be enough.

## Option A: leave the files where they are

Zero risk. The zones exist on the map and in the table above. Cost: the folder listing on GitHub still shows 19 files in one place.

## Option B: move the test bench into `engine/backtests/`

Move the 10 test-bench files. Leave the daily line and the two sealed scripts in `engine/`.

What it touches, measured on the current branch:

| Area | Change needed |
|---|---|
| Imports | The scripts import each other by bare name (`from factors import …` 11 times, `from roe_data` 9, `from reportlib` 7, `from paths` 4). Moved scripts need the parent folder on their import path, or `engine/` becomes a package. |
| `paths.py` | It finds data and reports from its own location. It needs one line changed if it moves. |
| CI (`.github/workflows`) | `py_compile engine/*.py` misses a subfolder. The step that imports `paths` and `reportlib` from `engine/` needs its working directory changed. |
| `tools/facts_lint.py` | 5 references to `engine/<file>` paths. |
| `research/ahp_analyze.py`, `tools/roe_selftest.py` | They add `engine/` to the import path; 9 path mentions between them. |
| Docs | 8 mentions of `engine/<file>` in `CHANGELOG.md`, `REPORT.md` and `0-if-you-have-no-idea/`. The facts lint will flag any that are missed. |
| The codebase map | Its guided tours name files by folder, so they need the new paths. |

Estimated effort: one person, about two hours, in a single pull request with CI green.

## Option C: also move the sealed scripts into `engine/sealed/`

Not recommended. To keep working after a move, `blind_test.py` and `backtest_sizing.py` would need their imports edited. They are the record of exactly what was run once. Editing them, even only the imports, weakens the claim that the sealed test is the code that produced the published result.

## Recommendation

**Option A now. Option B after the final submission, if the team still wants it.**

The gain from B is a tidier folder listing. The risk is breaking the daily run or CI a few weeks before the deadline, for a change that adds no feature and no finding. The map already gives a reader the three-zone view.

If the team prefers B sooner, the safe order is:

1. Branch from `main`. Move the 10 files with `git mv` so history follows them.
2. Fix imports and `paths.py`. Run every moved script once to confirm it still writes its report.
3. Update CI, `facts_lint.py`, `ahp_analyze.py` and `roe_selftest.py`.
4. Run the facts lint and fix the doc mentions it reports.
5. Do **not** run `blind_test.py` or `backtest_sizing.py`.
6. Rebuild the codebase map.

## Decision needed

- A, B or C?
- If B: who does it, and before or after the submission?
