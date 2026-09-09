# SETScout — An Explainable Stock Screener That Measured Itself and Published the Answer

**Course:** Data Science (01526125) — Term Project
**Team (8):** Paphangkorn Onrueang · Pakkapon [—] · [6 more members & IDs — roles in `docs/Team-Map.md`]
**Draft:** v1, 1 September 2026
**Live system:** https://oksoimcodingnow.github.io/atlas/setscout/
**Code:** `atlas/setscout/` — every number below regenerates from the scripts named beside it.

---

## Abstract

We built SETScout, a web tool that ranks ~95 Thai large-cap stocks on five
price-based factors, adapts the ranking to a user's risk profile, and explains
each recommendation in four plain sentences. We then asked the question most
student projects skip: **does it actually work?**

The answer is no, and establishing that carefully is the contribution.

Across 84 months of point-in-time backtesting, a stock's score has **no
relationship to whether it rises**: the measured up-rate is flat at roughly
47% across all ten score deciles. Buying the top 20% and holding trails simply
buying everything, and beats **0%** of randomly-selected portfolios. When one
weighting appeared to beat the market after roughly fifteen exploratory tests,
we pre-registered a single blind test on a period we had never examined; it
failed the pass mark we had written down in advance. Investigating the
benchmark itself, we found it inflated more than fourfold by survivorship bias
and a flawed averaging method — an error in our own earlier analysis, which we
quantify and correct here.

The system's value is therefore not prediction but **honest discovery**: a
shortlist with transparent scoring, quantified risk, and a confidence figure
that reports what was measured rather than what we hoped.

---

## 1. Question and motivation

Retail investing in Thailand grew sharply after 2020, and beginners face two
problems at once: too many stocks to evaluate, and advice that rarely says how
much to trust it. Commercial screeners output rankings with no accuracy claim;
brokerage notes state target prices with no error bar.

We asked two questions:

1. **Can a transparent, multi-factor screener help a beginner narrow SET100
   down to a handful of stocks worth researching?**
2. **Does that screener's ranking carry any predictive information — and can we
   tell the user honestly either way?**

The second question is the one that shaped the project. We committed early to
publishing whatever the evaluation returned, and the evaluation returned a null
result.

---

## 2. Data

**Source.** Daily adjusted closing prices from Yahoo Finance via the `yfinance`
library. Adjusted for splits and dividends.

**Universe.** SET100 constituents, maintained as a read-only list in
`universe.json`: **95 active tickers across 17 sectors**, plus a `retired`
section recording deliberate removals (currently INTUCH, delisted after its
2025 merger into GULF).

**Coverage rule.** A stock needs at least 130 trading days of history to be
scored. All 95 currently qualify; the last run scored **95 of 95** with none
skipped.

**Refresh.** A GitHub Action runs the engine daily at 11:00 UTC (18:00 Thailand,
90 minutes after the SET close so prices are final), then a health check
(`verify_today.py`) that fails loudly rather than publishing a broken file.

### 2.1 A data limitation we cannot fix, stated up front

Our universe is **today's** SET100. Every backtest therefore only ever holds
companies we already know survived to 2026. This is **survivorship bias**, and
it inflates every historical result.

We could not correct it — that requires point-in-time index membership data we
do not have — so we measured it instead. Section 6 reports the size.

---

## 3. Method

### 3.1 The five factors

Each is computed from price alone. This is deliberate: price data exists for
every listed stock with no gaps, whereas fundamentals are patchy for Thai
small-caps. The cost is that our factors measure less than their names suggest,
which we state plainly in Section 7.

| Factor | Formula | Measures |
|---|---|---|
| Momentum | `price / price 126 days ago − 1` | 6-month price change |
| Growth | `price / price 252 days ago − 1` | 12-month price change |
| Value | `−(price / 200-day average − 1)` | Cheapness vs its own recent average |
| Quality | `−(std of daily returns × √252)` | Annualised volatility |
| Health | `min(price / running peak − 1)` | Worst drawdown in one year |

Two conventions worth noting. **Value and quality are negated** so that higher
always means better — the raw quantities measure expensiveness and wildness
respectively. **Health needs no negation** because drawdowns are already
negative, so −8% correctly outranks −35%.

The `√252` in quality converts a daily standard deviation to an annual one.
Uncertainty grows with the square root of time, not linearly: a month is about
5.5× as uncertain as a day, not 30×.

### 3.2 Normalisation

Raw factors are incomparable — a 6-month return and a volatility figure are
different units. Two steps fix this:

1. **Winsorised z-score.** Each factor is centred and scaled by its standard
   deviation, then clipped to ±3 so one extreme stock cannot dominate.
2. **Sector neutralisation.** The sector mean is subtracted, for sectors with at
   least three members. A bank is judged against banks.

Step 2 was added after an early version returned a top-10 consisting almost
entirely of banks — low-volatility stocks were sweeping the quality factor
market-wide.

### 3.3 Three risk profiles

The same five factors are combined with three weight sets. A five-question quiz
maps the user to one.

| Profile | Momentum | Growth | Value | Quality | Health |
|---|---|---|---|---|---|
| Conservative | 5% | 5% | 20% | **40%** | **30%** |
| Balanced | 20% | 12% | 24% | 28% | 16% |
| Aggressive | **40%** | **30%** | 15% | 10% | 5% |

The composite is converted to a **percentile rank**, so a displayed score of 80
means "top 20% of this list," not an absolute grade. Verdicts threshold that
rank: top 20% → *Worth a look*, 45th–80th → *Wait*, below 45th → *Not now*.

**These weights are the one part of the system with no evidence behind them.**
Nobody has measured that quality should be 40% rather than 35% for a cautious
investor. Replacing them with values elicited from experts via AHP is the main
outstanding work (Section 9).

### 3.4 What re-weighting actually does

Taking PTT on 1 September 2026, sector-adjusted:

```
momentum −0.63   growth −1.07   value +0.92   quality +1.70   health +1.25
```

| Profile | Weighted total | Rank |
|---|---|---|
| Conservative | +1.15 | **#1 of 95** |
| Balanced | +0.64 | **#1 of 95** |
| Aggressive | −0.20 | **#71 of 95** |

The same stock, the same day, ranks 1st or 71st depending only on the weights.
GUNKUL — strong momentum, expensive, volatile — moves #65 → #1 in the other
direction.

This makes the system's nature explicit: **it holds no view on which stocks will
rise.** It has one opinion, about which *kind* of stock suits a given investor,
and expresses it by re-weighting five fixed numbers.

---

## 4. The product

The website reads a single precomputed file, `today.json`, so nothing is
calculated in the browser and no server is needed. Every recommendation is
delivered as four fixed sentences:

| Element | Example |
|---|---|
| **Verdict** | ✅ Worth a look |
| **Risk, in baht** | "A normal-bad month could drop ~9%, so put at most ฿30 of every 100" |
| **Because** | "Strong, stable earnings and a solid balance sheet" |
| **Trust label** | "Stocks scoring like this rose the next month 44% of the time — measured over 84 months, and the same across almost every score band" |

Risk uses a monthly Value-at-Risk, `1.645 × σ_daily × √21`, clamped to 6–35%,
converted into a suggested maximum position size.

The interface is bilingual (Thai/English), works in light and dark, and carries
an educational-use disclaimer on every card. Verdict wording avoids "buy" —
Thai uses *น่าสนใจ* ("worth a look") — because we are not licensed to give
investment advice.

---

## 5. Evaluation

All tests are **point-in-time**: at each month, stocks are scored using only
data available up to that month, and returns are measured strictly afterwards.
There is no look-ahead.

Each test also reports a **luck bar** — the share of 300 randomly-chosen
portfolios of the same size that our picks beat. This is the critical control.
Any strategy looks good in a rising market; the luck bar asks whether it beat
*random picking in that same market*.

### 5.1 Does the score predict direction? — `backtest.py`

For every stock in every month across 84 months (7,398 observations, 703–791
per decile), we recorded its score and whether it rose the following month.
Scores here use the **balanced** weights, which `backtest.py` hard-codes.

| Score decile | 0–10 | 10–20 | 20–30 | 30–40 | 40–50 | 50–60 | 60–70 | 70–80 | 80–90 | **90–100** |
|---|---|---|---|---|---|---|---|---|---|---|
| Up-rate | 46.1% | 50.4% | 47.6% | 46.1% | 48.7% | 48.2% | 48.4% | 44.9% | 47.1% | **44.2%** |

**Flat.** Every decile sits between 44% and 50% around a base rate of 47.2%,
with no gradient — and the top decile is the lowest of the ten.

A sub-50% base rate is normal, not a failure: monthly stock returns are
right-skewed, so a stock is slightly more often down than up. **The finding is
that the score does not move the number.**

This result is now published inside the product. The trust label shows the
measured up-rate for each stock's decile rather than a figure we invented.

### 5.2 Does buying the top 20% beat buying everything? — `backtest_hold.py`

The fair test: buy the picks and hold, as a real user would, rather than
churning monthly.

| Horizon | Picks | Buy & hold | Luck bar |
|---|---|---|---|
| 6 months | +0.8% | +3.4% | **0%** |
| 12 months | +1.5% | +8.2% | **0%** |

The picks trail, and beat **zero** of 300 random portfolios. Monthly rotation
(`backtest.py`) performs similarly: +13.1% against +44.0% for buy-and-hold, an
11% luck bar.

### 5.3 Does the risk-based sizing help? — `backtest_sizing.py`

Every test above buys the top 20% in **equal amounts**. That is not what the
product tells users to do: SETScout shows a per-stock cap — *"put at most ฿30 of
every 100 in this one"* — derived from the stock's volatility and scaled by risk
profile. That advice had never been tested.

It deserved its own test because it is the more defensible half of the product:
**risk control can work even when prediction does not.**

**Pre-registered before running.** `max_weight` is a cap, not a weight — the caps
do not sum to 100% and the app never says how many stocks to buy — so turning
caps into a portfolio requires a rule. We committed to one in advance:

```
weight_i = cap_i / sum(cap_j for j in picks)
```

Hold the same names as the equal-weight arm, allocate in proportion to each
stock's cap, fully invested. Because the cap falls as volatility rises, this is
inverse-volatility weighting — a recognised technique, not one invented for the
test. Two alternatives (cap-and-redistribute; buy-at-cap with cash remainder)
were named and rejected in the file so they could not be quietly tried later.

**The hypothesis was about risk, not return.** Sizing does not claim to earn
more, it claims you lose less. The committed pass mark: *maximum drawdown
improves by ≥ 20% relative to equal weight, at a return cost ≤ 2.0 points.*

**Result — primary window, 2016 to present, 127 monthly rebalances:**

| Profile | Max drawdown change | Return cost | Verdict |
|---|---|---|---|
| Conservative | −1.1% (slightly worse) | +0.5 pts | **not supported** |
| Balanced | −0.2% (unchanged) | +0.3 pts | **not supported** |
| Aggressive | +5.1% better | +2.0 pts | **not supported** |

All three fail the pre-set bar. The best case improves drawdown by 5.1% where
20% was required. The 1999–2014 robustness window agrees: improvements of 0.0%
to 1.3%.

**One thing did move.** Annualised volatility fell in every profile — most
clearly for aggressive, 17.5% → 16.5%. So the sizing rule is doing something
real; it is simply too small to matter for drawdown.

**Why we think that is.** Drawdown in a long-only equity portfolio is dominated
by market-wide falls, not by how weight is distributed within the basket.
Holding 19 names already captures most of the available diversification; tilting
weights among those 19 adds little when everything falls together. The 2016–2026
window contains the COVID crash, and no weighting scheme inside a fully-invested
equity book avoids that.

### 5.4 A limitation of the sizing test itself

Stated because it matters, and deliberately **not** used to re-run the test with
friendlier parameters — that would be moving the goalposts after seeing the
result.

Our test applies the caps to a 19-stock basket. But the app's advice is probably
not consumed that way. A beginner using SETScout likely buys **two to five**
stocks, and there the cap is doing quite different work: it protects against
putting everything into one volatile name. Concentration risk in a 3-stock
portfolio is a far larger effect than weight tilts across 19.

So the honest statement is: **as tested, on a 19-stock basket, risk-based sizing
does not meaningfully reduce drawdown.** Whether it helps the concentrated
portfolios real beginners hold is a separate question, requiring its own
pre-registered test with its own pass mark. It is the single most promising
piece of future work in this project.

### 5.5 Verdict counts cannot vary

All three profiles return exactly 20 BUY / 33 WAIT / 42 AVOID. This is
structural rather than coincidental: the verdict thresholds a percentile rank,
and a percentile always distributes identically. **Weights change which stocks
occupy each bucket, never how many.**

---

## 6. The blind test — our central methodological result

### 6.1 Why it was necessary

By 31 August we had run five backtest scripts across three profiles over
roughly the same decade — **about fifteen looks at one dataset**. In that
exploration the *aggressive* weighting appeared to beat buy-and-hold with a 96%
luck bar.

We could not report that as evidence. We had chosen which result to find
interesting *after* seeing it — the practice known as data snooping, and a
principal reason published findings fail to replicate.

### 6.2 Design, fixed before execution

Written into `blind_test.py` before it was first run:

- **Sealed period:** score months 1999-01 to 2014-12 — never previously examined
  in isolation
- **Development period:** 2016-01 onward — the contaminated decade, reported for
  contrast only
- **Gap:** 2015, so a 12-month hold beginning December 2014 cannot reach the
  development window
- **Weights:** frozen, copied verbatim from the live engine; not re-tuned
- **Pass mark:** beats buy-and-hold **and** achieves a luck bar ≥ 90%

Because three profiles are tested, a 90% threshold on the best of three
corresponds to roughly 73% under the null. The Šidák-corrected bar for a
genuine 90% claim across three profiles is **96.5%**, reported alongside.

### 6.3 Result

| Profile | Beat buy & hold? | Luck bar | Pass mark | Verdict |
|---|---|---|---|---|
| Conservative | yes | 100% | 90% | passed |
| Balanced | yes | 100% | 90% | passed |
| **Aggressive** | yes, barely | **81%** | 90% | **FAILED** |

Deliberately no return figures. The sealed period's absolute returns are on this
report's own *never quote* list (Appendix B) — averages of overlapping windows on
a survivor-only sample, against a benchmark 4.4× inflated. Every column above is
**ordinal**: did it beat the benchmark, and what share of 300 random portfolios
did it beat. Picks, benchmark and random books all face the identical
distortion, so the comparison survives even though the levels do not.

**The aggressive edge did not replicate.** 81% falls below the 90% bar set in
advance and far below the corrected 96.5%. A non-overlapping block check is
weaker still: aggressive beat buy-and-hold in **2 of 5** three-year blocks —
40%, below a coin flip. Re-measured on the longer history, the development
window yields only +0.2 points at a 56% luck bar, so the original result did not
survive even a change in how the window was defined.

### 6.4 Why we do not claim the profiles that passed

Conservative and balanced record 100% luck bars in the sealed period. We do not
present this as a finding, for two reasons.

**We did not predict it.** Announcing it now would repeat precisely the error
the blind test was built to catch.

**The bias is not neutral between profiles.** Survivorship selects for companies
that did not fail — which is exactly what the quality and health factors reward.
Conservative places 70% of its weight on those two, balanced 44%, aggressive
15%. A survivors-only sample structurally flatters the profiles that scored
best. Their apparent success is plausibly an artifact we cannot rule out.

---

## 7. Correcting our own error: the benchmark was inflated

The sealed period reported buy-and-hold averaging +41.1% per 12 months. No
market delivers that, and a team member flagged it as implausible. Investigating
produced two distinct errors, one methodological and one in our comparison.

| Measure | Annual | Type |
|---|---|---|
| As originally reported | +41.1% | average of 12-month returns — **not** a growth rate |
| Basket compounded, with dividends | +33.3% | CAGR |
| Basket compounded, price only | **+26.6%** | CAGR — comparable to the index |
| Real SET index, price only | **+9.4%** | CAGR |

**Error 1 — averaging overlapping windows.** The mean of 168 overlapping
12-month returns is not an annual growth rate. For a volatile series it sits
well above the compounded result.

**Error 2 — mismatched dividend treatment.** Our basket was dividend-adjusted
while the SET index is price-only. That accounts for **6.7 points per year** and
was our mistake, not bias.

The remaining **17.1 points per year** is the genuine like-for-like gap, and
even this mixes survivorship with an equal-weight-versus-cap-weight tilt, which
we cannot separate without market-cap history.

### 7.1 Measuring the bias directly

The most persuasive evidence is that the gap **shrinks as the problem shrinks**:

| Year | Stocks existing | Our buy & hold | Real SET index | Gap |
|---|---|---|---|---|
| 2001 | 37 of 95 | +97% | −9% | **+53** |
| 2002 | 38 of 95 | +59% | +5% | **+77** |
| 2006 | 48 of 95 | +54% | −12% | **+70** |
| 2013 | 55 of 95 | +13% | −13% | +20 |
| 2018 | 77 of 95 | +2% | −16% | **+3** |
| 2022 | 87 of 95 | −2% | +1% | **+5** |
| 2023 | 89 of 95 | −8% | −17% | **+6** |

When only ~40% of the list existed, gaps run +53 to +77 points. When ~92%
exists, +3 to +6. The bias is not an assumption but a measurement that decays
exactly as coverage improves. Reproduce with `python explore.py --years`.

**Consequence:** absolute return levels from before ~2015 are unusable. Internal
comparisons remain valid, because picks, benchmark and random portfolios all
face the identical distortion. Throughout this report we compare rows and never
quote levels.

---

## 8. Limitations

**The factor names promise more than the mathematics delivers.** "Quality" is
low volatility, "health" is shallow drawdown, "growth" is price change. None
touches revenue, profit or debt. Adding real fundamentals (P/E, ROE, earnings
growth) is the clearest next improvement.

**A one-year window measures recent calm, not resilience.** Quality and health
look back 252 days, so a company that survived every crisis since 2008 but had
one poor year scores below one that listed in 2024 and had a quiet ride.

**Conservative and balanced are barely distinguishable.** Top-10 overlap is
8/10, top-20 is 19/20, and they currently share an identical top five. Since the
quiz routes most users to balanced, the middle profile does little work.

**Survivorship bias is unfixable with our data**, as quantified above.

**Overlapping test windows are not independent observations.** 168 start-points
across 14 years overlap heavily, so effective sample size is far below the
nominal count.

**Only the balanced profile was calibrated.** `backtest.py` and
`backtest_hold.py` hard-code the balanced weights, so the flat ~47% up-rate and
the 0% luck bars are measured for *balanced* specifically. The three-profile
comparisons (`backtest_profiles.py`, `backtest_costs.py`, `backtest_long.py`,
`blind_test.py`) do cover all three. We expect the calibration result to hold
across profiles — they share identical factors and the same percentile
transform — but we have not measured it, and it should not be presented as
though we had. Extending calibration to all three is straightforward future
work.

**The weights are unmeasured.** See below.

---

## 9. Outstanding work

**AHP expert survey.** Ten pairwise factor comparisons on the Saaty 1–9 scale,
per investor profile, from 6–10 experts. Respondents failing a consistency ratio
of 0.10 are excluded and the exclusion count reported. Aggregation by geometric
mean.

This replaces the invented weights with elicited ones, and enables a sensitivity
analysis whose perturbation range is the **observed disagreement among experts**
rather than an arbitrary ±10%. Bootstrapping the respondents then yields a
defensible per-stock statement — *"appears in the top 10 under 87% of expert
weightings"* — which is a confidence figure derived from primary data we
collected ourselves.

---

## 10. Verdict

**SETScout does not beat buying the whole market, its score does not predict
direction, and its risk-based sizing does not meaningfully reduce drawdown.**
Both halves of the product were tested against pass marks fixed in advance, and
both fell short. We state this in the report, in the code, and in the product
itself.

We regard this as the project's strength. The contribution is not a profitable
screener but a **demonstrated method for finding out**, comprising:

1. Point-in-time evaluation with no look-ahead
2. A luck bar controlling for random selection, not merely for the market
3. Calibration measuring whether scores carry information at all
4. A pre-registered blind test with the pass mark fixed in advance
5. A second pre-registered test, of the risk sizing rather than the
   ranking, which also returned null
6. Quantified bias, including a correction to our own earlier analysis
7. A product that publishes its own null result instead of concealing it

The sequence that we consider the report's core: **fifteen exploratory looks
produced an apparent edge; a single pre-registered test on unseen data refuted
it; and investigating the benchmark revealed our own measurement to be more than
four times inflated.** Each step was recorded before its outcome was known.

Few results are more useful to a beginner than a tool that says clearly: *this
is a shortlist to research, not a prediction.*

---

## Appendix A — Reproducing every number

All scripts require the project virtual environment; the default `python` on the
development machine lacks pandas.

```bash
PY="C:\Users\HOME\.venvs\quant-project\Scripts\python.exe"

$PY run_today.py        # refresh today.json (95 stocks x 3 profiles)
$PY verify_today.py     # health check; exits 1 if the refresh is bad
$PY backtest.py         # calibration + luck bar   -> reports/backtest.md
$PY backtest_hold.py    # the fair hold test       -> reports/backtest_hold.md
$PY backtest_profiles.py# three profiles compared  -> reports/backtest_profiles.md
$PY backtest_costs.py   # after trading costs      -> reports/backtest_costs.md
$PY backtest_long.py    # 5y / 10y horizons        -> reports/backtest_long.md
$PY blind_test.py       # pre-registered, run once -> reports/blind_test.md
$PY backtest_sizing.py  # pre-registered sizing test -> reports/backtest_sizing.md
$PY explore.py --years  # bias, year by year
$PY explore.py 2005 2007# any period you like
```

Each report records its run date, parameters and reproduce command.

## Appendix B — Figures that must not be quoted

Included so no team member cites them by accident.

| Figure | Why unusable |
|---|---|
| Sealed-period returns (+60.2%, +57.9%, +44.1%) | Averages of overlapping windows on a survivor-only sample |
| Sealed buy-and-hold +41.1% | 4.4× reality; the index returned +9.4% |
| Full-window cumulative (+16,707%) and CAGR +22–25% | 25 years compounding on survivors only |
| Aggressive +164% net over 10 years | Same survivorship problem, same contaminated decade |
| Aggressive +8.8% vs +7.0%, 96% luck bar | Data-snooped; cite only as "where the hypothesis came from" |

**Safe to quote:** the calibration table, blind-test luck bars and verdicts, the
bias-decay table, and the profile-separation example. Each is either a null
result or an internal comparison, so the bias does not distort it.

---

## Appendix C — Related work in this repository

`quant-project/` contains the earlier rule-based trading research (trend and
mean-reversion strategies, a GBM Monte Carlo risk engine, 16-window
walk-forward, supervised meta-labeling, deflated Sharpe). Its conclusion
independently corroborates ours: a single held-out window showed Sharpe +0.93
that walk-forward exposed as luck at −1.17, positive in only 4 of 16 windows.

**Two methods, two codebases, the same verdict** — which is considerably
stronger than either alone.

> **Note for the team:** `quant-project/REPORT-draft.md` (555 lines, 13 July)
> predates the SETScout framing and treats the project as the trading-strategy
> work. It needs either merging into this document or explicitly retiring. That
> decision has not been made.
