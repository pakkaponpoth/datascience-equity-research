# 🚀 SETScout — quick status
*(the 30-second version · full state = `CONTINUE.md` · full design = `HANDOFF.md`)*

**Live:** https://setscout-th.web.app  ·  **Mirror:** https://oksoimcodingnow.github.io/atlas/setscout/

## 🎯 If you read one thing

Five findings, all measured, all reproducible:

1. **`p_win` was invented** — `0.44 + 0.22 × score`, shown as "Hit rate 66%". Measured up-rate is **flat ~47%**, with no trend from low to high scores (p = 0.53). *(first replaced with the measured figure, then removed from the product entirely on 16 Sep — a number identical for every stock does not belong next to one stock's name)*
2. **`value` was momentum negated** — correlation **−0.93**, beta **−1.00**. "Balanced" was conservative in disguise: 8/10 shared names, 0.07 on a 0→1 scale. Now 6/10 and **0.44**. *(fixed)*
3. **Nothing beats buy-and-hold** — not raw, not risk-adjusted (`ret/vol` 0.04–0.06 vs B&H 0.06), not at any of five rebalancing frequencies.
4. **The score doesn't predict direction** — decile up-rates all between 43% and 50% (p = 0.28), 6-month quintiles 50 / 52 / 49 / 48 / 51. Flat. *(re-measured 21 Sep)*
5. **Conservative won 2 of 11 years**, both falling markets. Best: 2018, **+1.7% while the market fell 13.3%**. Missed the 2020 recovery by 29 points.

*(Findings 3 and 5 were measured before 21 Sep, on the engine with the sector step, and have not been re-run.)*

**That is the thesis, not a failure.** SETScout = discovery + risk + explanation. Don't fake an edge.

## ✅ Done recently

- **The sector adjustment is gone** (21 Sep, team decision, trial 82 in the lab). Scores are now z-scored across all 95 stocks, the same group the rank "#k of 95" names. Measured on identical prices before shipping: **all 7 banks enter the conservative and balanced BUY lists**, banks hold 6 and 7 of those top 10s (none before), and balanced now shares 18 of its top 20 with conservative. Accepted and stated in REPORT 3.2. The backtests were re-run and look a little better — **not** evidence the change helped (same survivorship-biased window, after a model change); the verdict is unchanged. The normalisation now lives in one place, `factors.zscore`, instead of nine copies; only the two sealed one-shots keep the old step. The facts lint fails on any new "sector-neutral" claim.
- **ROE audited, repaired and self-tested — now 95 of 95** (21 Sep). BANPU wasn't a parser failure: its filings aren't indexed in SEC's archive at all, so it now comes from SET's own statements, cross-checked on PTT (7.92% from both). A fiscal-year-end rule fixed four companies that don't close in December — BTS had been showing +4.0% against a latest filed −2.0%. A quality gate withholds 16 values the data contradicts; 5 were repaired only where the next year's filing proves the figure. Against SET for the same fiscal years: **median gap 0.002 points over 282 stock-years**. `tools/roe_selftest.py` breaks 200 good rows on purpose on every PR: 99.5–100% caught, 0 false alarms, 0 wrong repairs.
- **The rank shows "of 95"** (18 Sep). Filtering to a sector used to renumber its best name to #1. And the rank carries no predictive signal — information coefficient +0.0055, t = 0.28 (re-measured 21 Sep without the sector step: +0.0050, t = 0.20) — so it ships as a list position, never a forecast.
- **`growth` → `ROE`** (16 Sep). The 12-month return overlapped the 6-month one at **+0.66**, so two of four slots asked one question. ROE, built from **1,591 annual filings** in SEC Thailand's archive, passed the independence screen (trial 79) and was **neutral on returns** (trial 80: +0.0%/yr, t = 0.01) — adopted for independence and interpretability, **not** for performance. Trial 81 settled which return kept its place: dropping the 6-month one costs 1.7%/yr, so the 12-month one was the replaceable slot.
- **The hit rate is gone from the product** (16 Sep) — and the "because" chips stopped claiming "strong, stable earnings" for a factor that only measures price volatility.
- **Firebase auto-deploys** (8 Sep). It never did before — the daily job committed data and stopped, so the live site fell a day further behind every day. Was 3 days stale when found.
- **The monitor stopped lying** — it blamed the cron for stale data when the cron was fine. It now compares Firebase against the source and names the real culprit.
- **`research/factors.py`** — one definition, eleven importers. Was copy-pasted into ten files, several falsely labelled "FROZEN - identical to run_today.py".
- **Pre-registered tests import a dated `FROZEN` snapshot**, so a weight change can't silently re-run a sealed one-shot.
- **`reportlib` stopped eating evidence** — a crashed run used to overwrite the last good report with its own traceback. Now writes `<slug>.FAILED.md`.
- **The questionnaire shows the real formulas** and how scores are z-scored (it also said sector-neutralised, until that step was dropped on 21 Sep). 45 questions per expert → **18**.
- **Deleted**: `gen_today.js` (a fourth copy of the engine, stale weights, known-bad tickers), `firestore.rules.txt` (implied a database that doesn't exist).

## ▶️ Do FIRST

1. **Collect the AHP answers.** The survey went out on 21 Sep (Growth → ROE fixed first; the facts lint now fails if the survey and `FACTORS` disagree). Answers set the real deadline, not the presentation date. When they arrive, save them as `research/ahp_responses.csv` (same columns as `ahp_responses_template.csv`) and run `python research/ahp_analyze.py`.
2. **Ask the repo owner to fix the branch rule** — `main` still requires the website-build checks, which never run on a pull request, instead of `checks`. Until that changes a green PR cannot merge.

## 🗓️ After the presentation (22 Sep)

1. **Momentum looks back 125 trading days; the docs say 126.** `run_today.py` computes `s.iloc[-1] / s.iloc[-126] - 1`, which is 125 steps. Measured: rank correlation with a true 126-day window **0.992**, and the BUY lists change by 0, 0 and 1 stock. Make the code match the documented definition, then `run_today.py` + `verify_today.py`. This is a correction, not a new model search, and it touches no pre-registered one-shot.
2. **The position cap has no recorded rationale.** `cap = 0.42 × (1 − risk/32)`, clamped to 8–40%, was carried over from the mock generator `gen_today.js` (31 Jul, since deleted); no test chose 0.42 or 32. The site then scales it by 0.6 / 1.0 / 1.35 per profile, clamped to 5–60%. The report now calls it an unvalidated heuristic (§4). Replacing it is a **new pre-registered trial**: write it into `TRIALS.md` before running anything, and **never re-run `backtest_sizing.py`**.
3. **`explore.py --years` gets no data for the real SET index any more** (the `REALindex` and `gap` columns print `nan` as of 21 Sep), so REPORT 7.1's bias table cannot be reproduced right now. The buy-and-hold column still matches the report. Find a working source for `^SET.BK` before anyone re-runs it.
4. **`ahp_analyze.py --demo` overwrites `reports/ahp_weights.json` with demo weights** — the same file the real analysis writes. Make `--demo` write somewhere else (or not at all) before the real answers arrive, so demo numbers can never be mistaken for the panel's.

## ⚠️ Do NOT

- **No more engine work.** The stopping rule fired in July; the blind test confirmed it independently.
- **Never re-run `blind_test.py` or `backtest_sizing.py`** after a model change. Pre-registered one-shots.
- **Never quote**: sealed-period returns, +41.1% sealed B&H, full-window CAGR, +164% net 10y. Survivorship-inflated — **only 4 of 95 tickers had data in 1999**.
- **Before adding anything**: does this duplicate a value that already exists? Five instances so far were exactly that — the tally is in `CONTINUE.md`.

*(Run with the venv — the default `python` has no pandas:*
`C:\Users\HOME\.venvs\quant-project\Scripts\python.exe run_today.py`*)*
