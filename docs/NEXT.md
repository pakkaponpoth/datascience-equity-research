# 🚀 SETScout — quick status
*(the 30-second version · full state = `CONTINUE.md` · full design = `HANDOFF.md`)*

**Live:** https://setscout-th.web.app  ·  **Mirror:** https://oksoimcodingnow.github.io/atlas/setscout/

## 🎯 If you read one thing

Five findings, all measured, all reproducible:

1. **`p_win` was invented** — `0.44 + 0.22 × score`, shown as "Hit rate 66%". Measured up-rate is **flat ~47%** across every decile, top decile the *lowest*. *(fixed)*
2. **`value` was momentum negated** — correlation **−0.93**, beta **−1.00**. "Balanced" was conservative in disguise: 8/10 shared names, 0.07 on a 0→1 scale. Now 6/10 and **0.44**. *(fixed)*
3. **Nothing beats buy-and-hold** — not raw, not risk-adjusted (`ret/vol` 0.04–0.06 vs B&H 0.06), not at any of five rebalancing frequencies.
4. **The score doesn't predict direction** — quintile up-rates 47 / 54 / 48 / 50 / 48. Flat.
5. **Conservative won 2 of 11 years**, both falling markets. Best: 2018, **+1.7% while the market fell 13.3%**. Missed the 2020 recovery by 29 points.

**That is the thesis, not a failure.** SETScout = discovery + risk + explanation. Don't fake an edge.

## ✅ Done recently

- **Firebase auto-deploys** (8 Sep). It never did before — the daily job committed data and stopped, so the live site fell a day further behind every day. Was 3 days stale when found.
- **The monitor stopped lying** — it blamed the cron for stale data when the cron was fine. It now compares Firebase against the source and names the real culprit.
- **`research/factors.py`** — one definition, eleven importers. Was copy-pasted into ten files, several falsely labelled "FROZEN - identical to run_today.py".
- **Pre-registered tests import a dated `FROZEN` snapshot**, so a weight change can't silently re-run a sealed one-shot.
- **`reportlib` stopped eating evidence** — a crashed run used to overwrite the last good report with its own traceback. Now writes `<slug>.FAILED.md`.
- **The questionnaire shows the real formulas** and says scores are z-scored and sector-neutralised. 45 questions per expert → **18**.
- **Deleted**: `gen_today.js` (a fourth copy of the engine, stale weights, known-bad tickers), `firestore.rules.txt` (implied a database that doesn't exist).

## ▶️ Do FIRST

1. **Send the AHP survey.** The only task needing other people's time — it sets the real deadline, not the presentation date.
2. **Build the bootstrap** in `ahp_analyze.py`. Its own docstring promises it and calls it the intended replacement for the invented `p_win`. The code does not exist.
3. **Say the holding period on the site.** Every backtest assumes 6–12 months; the page refreshes daily and shows a *monthly* risk number. That quietly invites monthly trading — the worst of the five frequencies we tested.
4. **Merge PR #1, then #2** on the team repo (#2 is stacked on #1).

## ⚠️ Do NOT

- **No more engine work.** The stopping rule fired in July; the blind test confirmed it independently.
- **Never re-run `blind_test.py` or `backtest_sizing.py`** after a model change. Pre-registered one-shots.
- **Never quote**: sealed-period returns, +41.1% sealed B&H, full-window CAGR, +164% net 10y. Survivorship-inflated — **only 4 of 95 tickers had data in 1999**.
- **Before adding anything**: does this duplicate a value that already exists? Four bugs so far were exactly that.

*(Run with the venv — the default `python` has no pandas:*
`C:\Users\HOME\.venvs\quant-project\Scripts\python.exe run_today.py`*)*
