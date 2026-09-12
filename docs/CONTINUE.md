# ▶️ SETScout — Current State & How to Continue
*(as of 9 Sep 2026 — read this first if you're picking up on a new PC. What changed and why = `CHANGELOG.md`. Full design = `HANDOFF.md`. The 30-second version = `NEXT.md`.)*

**Live (canonical):** https://setscout-th.web.app
**Mirror:** https://oksoimcodingnow.github.io/atlas/setscout/

---

# 📌 THE FINDINGS — this is the project

Everything below this section is machinery. **These five findings are the contribution.**
Each one is measured, reproducible, and survived being checked.

### 1. `p_win` was fabricated, and our own data already said so
The app computed `p_win = 0.44 + 0.22 × score` and displayed it as **"Hit rate 66%"**.
That is a straight line off the ranking — zero independent information.

Meanwhile `backtest.py` had already measured the truth into `calibration.json`, and its
own docstring said the file existed *"so run_today.py can stop faking p_win."* It was
never wired in.

| Score decile | 0–10 | 30–40 | 60–70 | 90–100 |
|---|---|---|---|---|
| **Measured up-rate** | 46.1% | 46.1% | 48.4% | **44.2%** |
| **What the app showed** | 44–46% | 51–53% | 57–59% | **64–66%** |

Flat at ~47% across all ten deciles, with the **top decile the lowest**. The displayed
number wasn't merely unvalidated — it was contradicted by our own file. *Fixed 30 Aug.*

### 2. One of our original five factors was another one negated
`value` was price versus its own 200-day average. Across the universe that correlates
**−0.93** with the 6-month return — 86% shared variance, regression beta **−1.00** on
z-scores. Both formulas divide today's price by where the price used to be; the 200-day
average sits a median of 3.2% from the price six months ago. One reports that ratio,
the other reports its negative.

It was also **misnamed**: this is mean reversion. Real value needs an external anchor
(earnings, book value) that a price-only engine does not have.

Because `value` outweighed `momentum` in balanced (.24 vs .20) the two cancelled and
value won the remainder. So "balanced" — the profile the quiz sends most users to — was
**conservative wearing a different label**: 8 of its top 10 names, and 0.07 on a
0=conservative → 1=aggressive scale. After removal: 6/10 and **0.44**. *Fixed 9 Sep.*

### 3. Nothing beats buy-and-hold. Not on any axis we can measure.

```
                ann ret   ann vol   max DD   ret/vol   ret/DD
conservative      0.7%     18.7%    -49.2%     0.04     0.01
balanced          1.1%     19.5%    -50.2%     0.06     0.02
aggressive        1.5%     23.1%    -49.0%     0.06     0.03
buy & hold        1.3%     22.2%    -54.4%     0.06     0.02
```

Conservative and balanced **do** genuinely cut volatility and drawdown — but they cut
return by more, so `ret/vol` gets *worse*. Aggressive edges B&H on raw return by 0.2
points with an identical `ret/vol`. That is a rounding difference, not an edge.

Five rebalancing frequencies (15 days → yearly) all lost after costs, and the
differences between them were **smaller than the noise between them**.

### 4. The score does not predict direction
Up-rate by score quintile, low → high: **47% · 54% · 48% · 50% · 48%**. Flat.
If the ranking worked, that line would slope.

### 5. Calendar years: positive often, better than the market rarely
Conservative was positive in **7 of 11 years** but beat the market in only **2** — both
falling markets. Its best year was 2018: **+1.7% while the market fell 13.3%**. It did
not protect in 2023 or 2024, and it missed the 2020 recovery by **29 points**.

> **This is the thesis, not a failure.** SETScout is **discovery + risk + explanation**,
> not a beat-the-market system. We have look-ahead-free proof that most simple rules
> lose to buy-and-hold, and we say so on the site. **Do NOT overfit to fake an edge.**

---

## 🔁 The failure mode we keep repeating

Five instances of the same thing — a value or intention recorded in one place and never
wired to the place that uses it:

1. **`calibration.json`** — measured, documented, never read by the engine *(fixed)*
2. **`ahp_analyze.py`'s bootstrap** — a whole docstring section explains why it matters. **The code was never written.** *(still missing)*
3. **The factor definition** — copy-pasted into ten files, several labelled `# FROZEN - identical to run_today.py` while being nothing of the kind *(fixed: `research/factors.py`)*
4. **`gen_today.js`** — a fourth copy of the engine in JavaScript, with stale weights and known-bad tickers *(deleted 9 Sep)*
5. **`HOW-IT-WORKS.md`** — kept telling readers `p_win` was "a placeholder formula" and listed wiring it under **Still to build**, two weeks after it was wired *(fixed 13 Sep)*

Noticing our own recurring failure mode is a stronger report finding than any single bug.
**Before adding anything: does this duplicate a value that already exists somewhere?**

---

## ✅ Where we are (all working)

- **`index.html`** — the site. Verdict + 4 sentences · filter by verdict + sector · TH/EN · light/dark · risk-quiz personalisation · "ⓘ How we score" panel · 💰 DCA calculator · `legal.html`
- **`universe.json`** — **the canonical stock list, read-only for the engine.** Edit here to add or remove a stock. Added 30 Aug so a failed fetch can no longer delete a ticker forever (it had already lost four).
- **`research/factors.py`** — **the single source of truth for `FACTORS` and `PROFILES`.** Eleven files import it. `factors.check()` raises at import if a weight set stops summing to 1. Pre-registered tests import a dated `FROZEN` snapshot instead of the live weights, so a weight change cannot silently re-run a sealed test.
- **`run_today.py`** — the engine: `universe.json` → yfinance → **4 factors** → z-score → sector-neutralise → weighted rank → `today.json`. `p_win` is the measured up-rate from `calibration.json`.
- **`verify_today.py`** — health check, runs **before** the commit step so a crashed engine fails loudly instead of committing nothing and reporting success.
- **`research/`** — backtests, blind test, sizing test, explorer, `expert-ahp.md` (**exists — 214 lines**, an earlier version of this file wrongly said it didn't), `ahp_analyze.py`, `reportlib.py`.
- **Deployment** — the daily Action now **deploys to Firebase**, gated on `FIREBASE_SERVICE_ACCOUNT`. Before 8 Sep it committed data and stopped; Pages updated itself, Firebase did not, and the live site fell a day further behind every day.
- **Monitoring** — `status.html` + a 30-minute GitHub probe that compares the Firebase copy against the source copy, so it can tell a dead scheduler from a missed deploy.

## 🖥️ How to run

```bash
# the default `python` here has NO pandas - use the venv
C:\Users\HOME\.venvs\quant-project\Scripts\python.exe run_today.py
C:\Users\HOME\.venvs\quant-project\Scripts\python.exe research/backtest.py
C:\Users\HOME\.venvs\quant-project\Scripts\python.exe research/ahp_analyze.py --demo
```

**Always `git fetch` before diagnosing anything about the workflow.** A past session
declared the Action dead from a local clone that was 22 commits behind.

## ▶️ What's next

1. **Send the AHP survey.** It is the only task that needs other people's calendar time, so it sets the real deadline. Four factors → 6 comparisons per profile, 18 per expert (was 45).
2. **Build the bootstrap** in `ahp_analyze.py` — resample experts 1000× for *"PTT appears in the top 10 under 87% of expert weightings."* Named in its own docstring as the intended replacement for the invented `p_win`, and still not written.
3. **Add a holding-period statement to the site.** Every backtest assumes 6–12 months, but the page refreshes daily and shows a *monthly* risk figure — which quietly invites the behaviour our own data says is worst (monthly rebalancing was the worst of five).
4. **Merge PRs #1 and #2** on the team repo. #2 is stacked on #1.
5. **Finish `REPORT.md`** — needs team review and real names/IDs.

## ⚠️ Do NOT

- **No more engine work.** The stopping rule fired in July and the blind test confirmed it independently. Tuning weights now undoes the discipline that *is* the contribution.
- **Never re-run `blind_test.py` or `backtest_sizing.py` after changing the model.** Both are pre-registered one-shots. That is why they import `FROZEN`.
- **Never quote these numbers**: sealed-period returns, +41.1% sealed buy&hold, full-window CAGR, +164% net 10y. All survivorship-inflated — the universe is *today's* SET100, and only **4 of 95 tickers had data in 1999** (65% by 2014). See `REPORT.md` Appendix B.

## 🗺️ Repo map

- **`pakkaponpoth/datascience-equity-research`** — the team's source of truth. Build team work here.
- **`oksoimcodingnow/atlas` → `/setscout/`** — the working copy **and** the deploy source for both live URLs. Iterate here, sync stable work to the team repo.
- **`oksoimcodingnow/setscout`** — a standalone split (73 commits, full history), created 8 Sep for experiments. **Not wired to anything.** Rewire the deploy to it only after the presentation.

## 🔒 Non-negotiables

- Disclaimer everywhere: **educational, not investment advice.**
- Never claim an edge you haven't shown. The trust label cites the **measured** up-rate (~47%, flat across every decile).
- Any AI-drafted code: **you must be able to explain every line.**
