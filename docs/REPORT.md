# SETScout — An Explainable Stock Screener That Measured Itself and Published the Answer

**Course:** Data Science (01526125) — Term Project
**Team (8):** Paphangkorn Onrueang · Pakkapon [—] · [6 more members & IDs — roles in `docs/Team-Map.md`]
**Draft:** v3, 7 November 2026 — AHP weights adopted (v2: 7 Nov; v1: 1 Sep 2026)
**Live system:** https://oksoimcodingnow.github.io/atlas/setscout/
**Code:** `atlas/setscout/` — every number below regenerates from the scripts named beside it.

---

## Abstract

We built SETScout, a web tool that ranks 95 Thai large-cap stocks on four
factors (three from price, one from company filings), adapts the ranking to a user's risk profile, and explains
each recommendation in four plain sentences. We then asked the question most
student projects skip: **does it actually work?**

The answer is no, and establishing that carefully is the contribution.

Across 83 months of point-in-time backtesting, a stock's score has **no
relationship to its next-month return**: the information coefficient is
+0.013 (t = 0.54), statistically zero. Buying the top 20% and holding trails simply
buying everything, and beats at most **4%** of randomly-selected portfolios. When one
weighting appeared to beat the market after roughly fifteen exploratory tests,
we pre-registered a single blind test on a period we had never examined; it
failed the pass mark we had written down in advance. Investigating the
benchmark itself, we found it inflated more than fourfold by survivorship bias
and a flawed averaging method — an error in our own earlier analysis, which we
quantify and correct here.

The system's value is therefore not prediction but **honest discovery**: a
shortlist with transparent scoring, quantified risk, and a plain account of
what was measured rather than what we hoped. The factor weights come from an
expert survey (AHP); one expert passed the consistency test, so they are a pilot,
not a consensus, and every result above holds with both them and the earlier
team-set weights (Section 9).

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

### 3.1 The four factors

Three are computed from price alone, which is deliberate: price data exists for
every listed stock with no gaps, whereas fundamentals are patchy for Thai
small-caps. The cost is that those three measure less than their names suggest,
which we state plainly in Section 8. The fourth, ROE, is read from the companies'
own filed accounts — Section 3.5 explains where it came from and what replacing
a price factor with it did and did not achieve.

| Factor | Formula | Measures |
|---|---|---|
| Momentum | `price / price 126 days ago − 1` | 6-month price change |
| ROE | `net profit to owners / average shareholders' equity` | Profitability on the owners' capital |
| Quality | `−(std of daily returns × √252)` | Annualised volatility |
| Health | `min(price / running peak − 1)` | Worst drawdown in one year |

Two conventions worth noting. **Quality is negated** so that higher always
means better — raw volatility measures wildness, and the calmer stock should
score higher. **Health needs no negation** because drawdowns are already
negative, so −8% correctly outranks −35%.

The `√252` in quality converts a daily standard deviation to an annual one.
Uncertainty grows with the square root of time, not linearly: a month is about
5.5× as uncertain as a day, not 30×.

**The backtests sample these factors monthly; the live list uses daily prices.**
Every backtest in this report computes the price factors from month-end prices:
momentum over six monthly steps, quality from the volatility of twelve monthly
returns × √12, health as the worst fall across twelve month-ends. The table above
gives the daily formulas the site uses. We measured the gap on the same twelve
month-ends: the two rankings correlate at about **0.91**, and the monthly version
contains **72%** of the live BUY list for conservative, **79%** for balanced and
**91%** for aggressive. They are the same factors sampled at a different
frequency, so the backtests describe the live product closely but not exactly.

### 3.2 Normalisation

Raw factors are incomparable — a 6-month return and a volatility figure are
different units. One step fixes this: a **winsorised z-score**. Each factor is
centred on the mean of all 95 stocks and scaled by their standard deviation,
then clipped to ±3 so one extreme stock cannot dominate.

**A second step, sector neutralisation, was removed on 21 September 2026.** From
July, each z-score also had its sector's mean subtracted (for sectors with at
least three members), so a bank was judged against banks. It had been added
after an early version returned a top 10 made almost entirely of banks. The team
removed it because the product ranks every stock "#k of 95" across the whole
universe, and a score built sector by sector does not compare a stock with all 95.

We measured the consequence on identical prices before it shipped (trial 82).
The early problem returns, and it is accepted rather than hidden:

| Profile | BUY names kept (of 20) | Largest sector in the BUY list | Banks in the top 10 |
|---|---|---|---|
| Conservative | 8 | Commerce 4 → **Banking 7** | 0 → **6** |
| Balanced | 11 | Commerce 4 → **Banking 7** | 0 → **7** |
| Aggressive | 15 | Utilities 4 → Banking 4 | 0 → 1 |

All seven banks in the universe entered the conservative and balanced BUY
lists under the team weights; under the AHP weights (7 Nov 2026) six of the seven do. Banks have the calmest prices, and those two profiles weight calm prices
most. A bank-heavy conservative list therefore reflects one sector's low
volatility, not a diversified selection, and a reader should treat it that way.

### 3.3 Three risk profiles

The same four factors are combined with three weight sets. A five-question quiz
maps the user to one.

| Profile | Momentum | ROE | Quality | Health |
|---|---|---|---|---|
| Conservative | 5.5% | 11.8% | 26.2% | **56.5%** |
| Balanced | 9.6% | 20.9% | 20.9% | **48.7%** |
| Aggressive | **56.0%** | 24.9% | 9.5% | 9.5% |

The composite is converted to a **percentile rank**, so a displayed score of 80
means "top 20% of this list," not an absolute grade. Verdicts threshold that
rank: top 20% → *Worth a look*, 45th–80th → *Wait*, below 45th → *Not now*.

**These weights come from the AHP expert survey (Section 9).** They are the
principal-eigenvector weights of Expert E01, the one respondent who passed the
consistency test, and they replaced the team's own weights on 7 November 2026.
One expert is a pilot, not a consensus: the weights are elicited rather than
invented, but they rest on a single person's judgement.

> **Until 7 Nov 2026 the engine used weights the team set:** conservative
> quality 50% / health 38% / momentum 6% / ROE 6%; balanced quality 37% /
> momentum 26% / health 21% / ROE 16%; aggressive momentum 47% / ROE 35% /
> quality 12% / health 6%. Section 9 compares the two sets.

### 3.4 What re-weighting actually does

Taking PTT on 1 September 2026, z-scored across all 95 stocks:

```
momentum −0.03   roe −0.25   quality +1.41   health +1.62
```

| Profile | Weighted total | Rank of 95 |
|---|---|---|
| Conservative | +1.25 | **#4** |
| Balanced | +1.03 | #5 |
| Aggressive | +0.21 | #26 |

> **Re-derived 2026-11-07 with the AHP weights** by `engine/rederive_section34.py`, which
> reproduces `run_today.py`'s pipeline exactly (126/252-day windows, ≥130 days of history,
> winsorised z-scores across all 95) on prices truncated at 1 Sep 2026 — 95 of 95 stocks
> scored. The weighted totals follow from the z-scores and the weights in Section 3.3 to
> within 0.01 of rounding, so they are checkable by hand. Yahoo's adjusted prices changed
> between downloads: PTT's momentum z-score was −0.19 on 4 Oct and is −0.03 now.
> **History:** with the team weights (4 Oct download) PTT ranked #4, #7 and #40, and GUNKUL
> #53, #13 and #2. With the sector step (before 21 Sep) PTT ranked #2, #3 and #47. Under the
> **old model, before `value` was removed on 9 Sep,** these ranks were #1, #1 and #71: balanced
> agreed with conservative, which is exactly what the value/momentum cancellation produced.
> With four price factors they were #1, #5 and #77; replacing growth with ROE moved PTT up
> under the aggressive weights (#77 → #47), because its 12-month price change was poor while
> its return on equity is ordinary rather than bad.

The same stock, the same day, ranks **4th or 26th** depending only on the weights.
GUNKUL — strong momentum (+2.71) but volatile — runs the other way:
**#37 under conservative, #29 under balanced, #2 under aggressive.**

This makes the system's nature explicit: **it holds no view on which stocks will
rise.** It has one opinion, about which *kind* of stock suits a given investor,
and expresses it by re-weighting four fixed numbers.

---

### 3.5 Replacing growth with ROE — and why it is not a performance claim

The four factors above shared a weakness: all of them were price. Momentum and
growth shared more than that. Measured across 62 non-overlapping three-month
periods, the 6-month and 12-month returns correlate **+0.66** — inside the
±0.80 line we use to call two factors duplicates (Section 7), but close enough
that the engine was spending two of its four slots on one idea.

**The data source.** Return on equity is

```
ROE = net profit attributable to owners of the parent
      ÷ ((shareholders' equity this year end + last year end) / 2)
```

Profit is earned across a year while equity is a snapshot on one day, so the
denominator is the average of the two year-ends. "Attributable to owners of the
parent" matters: a company consolidating a subsidiary it owns 60% of reports
all of that subsidiary's profit, and the 40% belonging to other people has to
come out. Using the wrong line makes CPALL, which owns part of Makro, read 7.4%
instead of 17.0%.

Yahoo Finance and the SET website publish three to five years of this. We needed
decades, so we read it out of the annual statements in **SEC Thailand's
disclosure archive**, which holds the spreadsheet attached to every filing back
to about 2000.

| | |
|---|---|
| Annual filings examined | 1,741 |
| Stock-years read from SEC filings | **1,583 (91%)** |
| Stock-years filled from SET's own statements | 3 (BANPU, GULF and TIDLOR, fiscal 2025) |
| Companies covered | **all 95** |
| Period | 2001–2026; 54 companies with 15 years or more |
| Published after the quality gate | **1,570 of 1,586** — 16 withheld as extraction failures |
| Agreement with SET's own figures, same fiscal year | **median gap 0.002 points** over 282 stock-years; 96.1% within 2 points |
| Agreement with Yahoo on the values the site shows | 92 of 95 within 2 points |

The 150 unread filings split into 91 whose row labels the parser did not
recognise and **58 that exist only as Word or PDF documents**, which is why 100%
is not reachable by code alone. Two extraction bugs were found and fixed: MEGA
reported an ROE of 9,959% because its filing states profit in baht and equity in
thousands, and CRC reported 25,436,242% because its income statement says
"million Baht" where its balance sheet says only "Baht". After reading the unit
words in each sheet header and treating a bare "Baht" as unknown, impossible
values fell from 13 to 0.

Where our figure and Yahoo's disagree materially, ours is the one to prefer:
for TRUE's 2022 year we read **−5.6%** against Yahoo's **−30.0%**, because the
2022 accounts were restated after the DTAC merger and Yahoo carries the restated
number. An investor standing in 2023 could only have seen the original.

**Point-in-time availability.** Thai listed companies must file audited annual
statements within three months of their year end, so a fiscal year's ROE is
treated as unavailable until **three months after that year ends**. For the 91
companies that close in December this is 1 April of the following year, so a
backtest standing in February 2013 scores on 2011's ROE, not 2012's.

Until 21 September 2026 that December date was hard-coded for everyone. Four
companies close in another month — AEONTS in February, BTS and VGI in March, AOT
in September — and for them the rule withheld a figure we already held for up to
a year. BTS was showing **+4.0%** when its latest filed year read **−2.0%**, and
VGI **+1.7%** against **−3.0%**. The year ends were read off the period-end dates of
published balance sheets for all 95 companies rather than typed from memory.

**The tests, pre-registered before they ran.**

| Trial | Hypothesis | Result |
|---|---|---|
| 79 | ROE is not a duplicate: \|r\| < 0.80 against every live factor, judged before any return is examined | **Pass** — −0.04 momentum, −0.02 growth, +0.11 quality, +0.04 health |
| 80 | ROE replaces growth at the same weight, and beats the current engine with t > 2.0 and a Sharpe above the deflated bar of 0.82 | **Fail** — +0.0%/yr, t = 0.01 |
| 81 | ROE replaces momentum instead, since the two returns overlap and only data should choose | **Fail** — −1.7%/yr, t = −1.14 |

Trial 81 is the one that settles which return keeps its slot. Removing the
6-month return costs 1.7 points a year; removing the 12-month one costs nothing
measurable. The 12-month return is therefore the interchangeable factor, and it
is the one that was replaced.

Because roughly 9% of the filings could not be read, the same comparison was
re-run under every treatment that could plausibly change it — these are
robustness checks on one hypothesis, not five new trials:

| Treatment | Difference per year | t |
|---|---|---|
| Baseline | +0.0% | 0.01 |
| Only the 51 companies with an unbroken record | −0.0% | −0.01 |
| Filings assumed available 1 July rather than 1 April | −0.4% | −0.25 |
| The 12 stock-years that disagree with Yahoo removed | +0.2% | 0.18 |
| ROE winsorised at the 5th/95th percentile each period | +0.3% | 0.22 |

Every t lies between −0.25 and +0.22, against a pass mark of 2.0. The remaining
data errors cannot flip the verdict.

**What we claim, and what we do not.** We do not claim that adding ROE improved
returns. It did not: the effect is indistinguishable from zero, and an earlier
run that appeared to show **+0.8%/yr (t = 0.65)** was measured on the data before
the unit bugs were fixed — the entire apparent gain was an artifact, which is
its own small lesson about weak positive results. The change was adopted because
it costs nothing measurable and buys two things: the four factors become four
different questions rather than three, and one of them finally comes from the
company's accounts instead of its price chart.

**Missing values.** A stock with no usable ROE is scored at the universe median
on that factor rather than dropped — a deliberate "no opinion" that neither
rewards nor punishes it, and that keeps the live list and the backtests doing
the same thing. The card shows a dash rather than a number the company never
reported. Since 21 September no card needs one: all 95 carry a filed figure.

#### 3.5.1 How the ROE data was checked

The trials above were run on the data as first extracted. An audit on 20–21
September then checked the data itself, by five approaches that could each fail
independently. About 1% of rows changed; none of the pre-registered verdicts
depends on them.

**BANPU was an indexing gap, not a parse failure.** A search for its filings
returns one 2026 Q2 document whatever is asked, and one year at a time returns
none at all, where PTT returns 208 documents across 26 years. The figures come
instead from SET's own factsheet, which publishes "Shareholders' Equity" and
"Net Profit : Owners Of The Parent" as structured lines. The two sources were
compared before one was trusted to fill the other: PTT's fiscal 2025 is **7.92%**
from both.

**A quality gate withholds what the data itself contradicts.** A value is
withheld in three cases: its magnitude exceeds 100%, which no annual ROE reaches;
it repeats the same company's previous filing exactly; or it is near zero (under
0.5%) *and* more than fifty times smaller than the median of the company's nearby
filings — up to two on each side, counted in filing order, so a gap in the
record widens the comparison rather than shrinking it. Near zero alone would
suppress real break-even years, so that rule needs both conditions.
Sixteen values are withheld. Some are probably real — CRC 2020–21 and PTTGC 2020
fell close to zero in the pandemic — and suppressing them is a known cost of a
rule that cannot tell a catastrophic year from a parse error.

**Five values were repaired, only where the repair could be proven.** The parser
had been dividing net profit by up to a million whenever a ratio exceeded 1.0,
which is how AOT's 2005 became 0.0001%. Each filing states last year's profit
beside this year's; that comparative now anchors the repair. AOT 2005 is
**12.05%** from its 2006 filing's statement of it, SCB 2012 **26.06%** once an
equity of 154 trillion baht — eight times Thailand's GDP — is read in thousands.
Two further repairs landed in a plausible range and were rejected anyway, because
the corrected equity contradicted the company's own balance sheets in adjacent
years.

**The checks were themselves tested.** `tools/roe_selftest.py` breaks 200 rows
the gate accepts with the four faults found in the real data, then measures what
happens. It catches **99.5–100%** of each, wrongly flags **0 of 1,570** untouched
rows, restores **84.9%** of caught rows to their exact original value, declines
the remaining 15.1%, and repairs **none** to a wrong value. It runs on every pull
request.

---

## 4. The product

The website reads a single precomputed file, `today.json`, so nothing is
calculated in the browser and no server is needed. Every recommendation is
delivered as a small fixed set of sentences:

| Element | Example |
|---|---|
| **Rank** | "#7 / 95" — its position among all scored stocks today, never among the ones currently filtered on screen |
| **Verdict** | ✅ Worth a look |
| **Risk, in baht** | "A normal-bad month could drop ~9%, so put at most ฿30 of every 100" |
| **Because** | "Up over the last 6 months and high return on equity" |
| **Latest ROE** | "18.0%" — the figure from the company's own accounts, or a dash where no filing could be read |

The two reasons are the factors that moved the stock's score most under the
active profile (weight × z-score), and a factor is called a strength only if
the stock is above the universe average on it. Until 7 November 2026 the chips
were simply the highest and lowest raw z-scores, ignoring sign and weight: on
the 6 November file 13–19 of 190 reasons per profile were the wrong way round
(SINGER, an aggressive pick, read "high return on equity" beside an ROE of
1.4%). Scores, ranks and verdicts were never affected. The page header shows
the date of the closing prices used, which can be one trading day behind the
run date (`prices_asof` in `today.json`).

Risk uses a monthly Value-at-Risk, `1.645 × σ_daily × √21`, clamped to 6–35%,
converted into a suggested maximum position size by `0.42 × (1 − risk/32)`,
clamped to 8–40%, which the site then scales by 0.6 / 1.0 / 1.35 for the three
profiles (clamped to 5–60%). **These constants are an unvalidated heuristic:** no
test chose 0.42 or 32 — they were carried over from an early mock-data
generator. §5.3 tests the rule as it stands; it does not justify the numbers.

The interface is bilingual (Thai/English), works in light and dark, and carries
an educational-use disclaimer on every card. Verdict wording avoids "buy" —
Thai uses *น่าสนใจ* ("worth a look") — because we are not licensed to give
investment advice.

---

## 5. Evaluation

All tests are **point-in-time**: at each month, stocks are scored using only
data available up to that month, and returns are measured strictly afterwards.
There is no look-ahead. The price factors are sampled at month-ends, not daily;
§3.1 measures how far that moves the ranking.

Each test also reports a **luck bar** — the share of 300 randomly-chosen
portfolios of the same size that our picks beat. This is the critical control.
Any strategy looks good in a rising market; the luck bar asks whether it beat
*random picking in that same market*.

### 5.1 Does the score order returns? — `backtest.py`

For every month across 83 complete months (Nov 2019 – Oct 2026; 7,347
stock-months), we scored each stock and ranked it against its return the
following month. The standard measure is the **information coefficient** (IC):
the rank correlation between this month's score and next month's return,
computed per month and averaged. Scores here use the **balanced** weights,
which `backtest.py` hard-codes.

| | |
|---|---|
| Months measured | 83 |
| Mean information coefficient | **+0.0128** |
| t-statistic | **+0.54** |
| Months with a positive IC | 49 of 83 (59%) |
| Month-to-month standard deviation | 0.215 |

A useful equity signal runs an IC of roughly **0.03 to 0.05**. Ours is less than
half the bottom of that range and indistinguishable from zero (t = +0.54). (With
the old team weights on the same data: +0.0080, t = +0.32, 42 of 83 months. Before
the sector step was removed on 21 Sep: +0.0055, t = +0.28, 43 of 83 months — no
different.) `backtest.py` computes
this, so the figure cannot drift out of step with the engine.

**Why this matters for the product.** The site displays a stock's rank among the
95. That is a description of where it sits on today's list, and the wording says
so. It is not a forecast, and this measurement is why: the ordering carries no
information about next month.

This result is also why the product shows **no hit rate**. Until 16 September
2026 the app showed a per-stock "hit rate", first an invented formula and then a
measured figure that came out the same for every stock. It was removed: a number
shown next to one stock's name invites a forecast reading the tests rule out.

### 5.2 Does buying the top 20% beat buying everything? — `backtest_hold.py`

The fair test: buy the picks and hold, as a real user would, rather than
churning monthly.

| Horizon | Picks | Buy & hold | Luck bar |
|---|---|---|---|
| 6 months | +3.7% | +4.9% | **4%** |
| 12 months | +7.7% | +9.8% | **3%** |

The picks trail, and beat at most **4%** of 300 random portfolios. Monthly
rotation (`backtest.py`) performs similarly: +15.7% against +44.0% for
buy-and-hold, a 13% luck bar.

> **Re-measured 7 Nov 2026 with the AHP weights.** The old team weights on the
> same download gave +3.4% and +7.4% (luck bars 1% and 2%), and +22.7% monthly
> with a 22% luck bar. The two weight sets give the same verdict: the picks trail
> buy-and-hold and sit inside luck. On 21 Sep (team weights, data to Aug 2026) the
> figures were +2.4% / +5.9% against +3.9% / +8.8%.

> **Re-measured 21 Sep 2026, after the sector step was removed (Section 3.2).**
> The picks now trail by less: the engine before gave +0.8% and +2.8%, luck bars
> of 0%, and +14.4% monthly with an 8% luck bar. **This is not evidence that
> removing the step helped.** It was removed for a design reason, and this is a
> re-run on the same survivorship-biased window after a model change — the
> situation the deflated Sharpe bar (Section 3.5) and the blind test (Section 6)
> exist to guard against. The verdict is
> unchanged: the picks still trail buy-and-hold and still sit inside luck. The
> 16 Sep figures (ROE engine) and the price-only engine's (+1.5% / +8.2% at 12
> months, +13.1% vs +44.0% monthly) gave the same verdict.

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
In the frozen model the test ran on, conservative places 70% of its weight on
those two, balanced 44%, aggressive 15%. A survivors-only sample structurally
flatters the profiles that scored best. Their apparent success is plausibly an
artifact we cannot rule out.

**The live AHP weights have no sealed test.** Both one-shots test the frozen
31 August model by design and cannot be re-run without becoming the data snooping
they exist to prevent. The AHP weights tilt further toward the calm-survivor
factors (83%, 70% and 19% of weight on quality and health), so the bias above
would flatter them more, not less.

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

> **Reproducibility note (7 Nov 2026).** Since 21 September Yahoo returns a
> single row for `^SET.BK`, so the *Real SET index* column can no longer be
> downloaded and `explore.py --years` prints `nan` there. The table stands as
> measured on 31 August–1 September 2026; the buy-and-hold column still
> reproduces. `TDEX.BK` (the SET50 ETF) has daily history only from 2008, so it
> cannot stand in for 2001–2006.

**Consequence:** absolute return levels from before ~2015 are unusable. Internal
comparisons remain valid, because picks, benchmark and random portfolios all
face the identical distortion. Throughout this report we compare rows and never
quote levels.

---

## 8. Limitations

**Three of the four factor names still promise more than the mathematics
delivers.** "Quality" is low volatility and "health" is shallow drawdown -
neither touches revenue, profit or debt. ROE, added on 16 September 2026, is the
first factor that does (Section 3.5), and it did not improve returns; P/E and
earnings growth are the obvious next candidates. The interface wording was
corrected at the same time: the "because" chips used to say "strong, stable
earnings" for a factor that only ever looked at price volatility.

**A one-year window measures recent calm, not resilience.** Quality and health
look back 252 days, so a company that survived every crisis since 2008 but had
one poor year scores below one that listed in 2024 and had a quiet ride.

**Balanced now sits almost on top of conservative.** Under the original
five-factor model the two were barely distinguishable — top-10 overlap 8/10,
top-20 19/20 — because value and momentum cancelled; removing value fixed the worst
of it. The AHP weights bring it back: the expert puts health first in both profiles
(0.565 and 0.487), so on 7 Nov 2026 balanced shares **9 of its top 10 and 18 of its
top 20** with conservative, against 1 of 10 and 6 of 20 with aggressive. Six of the
seven banks sit in both top 20s. In practice the product offers two distinct lists,
cautious and aggressive, plus a balanced list that is a near-copy of the cautious
one. A larger panel might separate them; with one expert we report it as found.

**Survivorship bias is unfixable with our data**, as quantified above.

**"Buy and hold" means two slightly different things in two scripts.**
`backtest_hold.py` averages each stock's own 12-month return (a true
buy-and-hold basket: +9.8% on 7 Nov). `backtest_profiles.py` compounds the
average monthly return of all stocks, an equal-weight basket rebalanced every
month (+8.6%). Each script compares its picks with its own benchmark, so every
"vs B&H" column is internally fair, but the two benchmark levels should not be
quoted side by side.

**Overlapping test windows are not independent observations.** 168 start-points
across 14 years overlap heavily, so effective sample size is far below the
nominal count.

**Only the balanced profile was tested for ordering.** `backtest.py` and
`backtest_hold.py` hard-code the balanced weights, so the near-zero IC and
the 3–4% luck bars are measured for *balanced* specifically. The three-profile
comparisons (`backtest_profiles.py`, `backtest_costs.py`, `backtest_long.py`,
`blind_test.py`) do cover all three. We expect the null result to hold
across profiles — they share identical factors and the same percentile
transform — but we have not measured it, and it should not be presented as
though we had. Extending these tests to all three is straightforward future
work.

**The weights rest on one expert.** The AHP survey had two respondents and one
passed the consistency test; Section 9 sets out what that does and does not support.

---

## 9. Expert weights: the AHP survey the engine now uses

### 9.1 Result (survey sent 21 Sep 2026, closed 6 Nov 2026; adopted 7 Nov 2026)

Two experts answered the 18 comparisons (six pairs per profile, Saaty 1–9).
The analysis, the raw judgments and the Excel workbook are in
`research/ahp-factor-weights/` (PR #10, principal-eigenvector weights):

| Profile | Momentum | ROE | Quality | Health | CR |
|---|---|---|---|---|---|
| Conservative | 0.055 | 0.118 | 0.262 | **0.565** | 0.043 |
| Balanced | 0.096 | 0.208 | 0.208 | **0.487** | 0.057 |
| Aggressive | **0.560** | 0.249 | 0.095 | 0.095 | 0.016 |

Expert E01 passed the consistency test in all three profiles. Expert E02
answered 7 ("very strongly more important") on all 18 questions, with the same
winner in every profile: CR 0.379, so E02 is excluded. `research/ahp_analyze.py`
(normalised row geometric mean) gives the same weights to within 0.4 points.

That leaves one consistent respondent per profile, below the three that the
small-panel rule asked for before elicited weights replace the team's
(`MIN_KEPT = 3`, fixed on 3 Oct before any answer was analysed). **On 7 November
2026 the team adopted E01's weights in the engine anyway.** We state the
trade-off plainly: elicited weights from one consistent expert replace weights
nobody elicited at all, but one person's judgement is a pilot, not a consensus,
and the rule we wrote down in advance was set aside to do it.

What changed: the direction matches the old team weights (momentum leads for
aggressive, the two risk factors for conservative), but E01 puts far more
weight on health (drawdown) than on quality (volatility), most visibly in
balanced (0.487 against the team's 0.21). On the 95 stocks scored on
7 November 2026 (closes of 6 November), the AHP weights keep **8 of each
profile's top 10** that the team weights gave, and 18, 17 and 17 of the
conservative, balanced and aggressive top 20s.

Every rerunnable test was re-measured with the AHP weights on 7 November 2026
(Sections 5.1–5.2 and the profile, cost and long-horizon reports). Each was also
re-run with the old team weights on the same download, so the comparison is
like for like:

| Test (7 Nov 2026, same download) | Team weights | AHP weights |
|---|---|---|
| Information coefficient, balanced | +0.0080 (t = +0.32) | +0.0128 (t = +0.54) |
| Top 20% held 12 months vs +9.8%, balanced (luck bar) | +7.4% (2%) | +7.7% (3%) |
| Monthly rotation vs +44.0%, balanced (luck bar) | +22.7% (22%) | +15.7% (13%) |
| 12-month hold vs +8.6%, conservative (luck bar) | +6.6% (2%) | +7.1% (6%) |
| 12-month hold vs +8.6%, balanced (luck bar) | +7.2% (8%) | +7.5% (11%) |
| 12-month hold vs +8.6%, aggressive (luck bar) | +11.1% (100%) | +12.9% (100%) |

Nothing in the verdict changes. The score still does not order next-month returns, and
the balanced picks still trail buy-and-hold inside the luck bar. Aggressive is
again ahead on this window, by more than before; it is the same survivor-only
decade examined about fifteen times, on which the sealed test (Section 6) already
refused that result. The expert gave the weights without seeing any backtest, so
they were not tuned to it, but that does not make the window clean. The figure is
listed in Appendix B.

The two sealed one-shots were **not** re-run (Section 6): they test the frozen
31 August model by design, so the AHP weights have no out-of-sample test.

The survey form's answers name the ROE factor "Growth", and PR #10 maps it to ROE. <!-- facts-lint: ignore -->
The questionnaire in `research/expert-ahp.md` switched that factor from the
12-month return to ROE on 21 Sep, the day the survey went out.

### 9.2 What a full panel would add

**AHP expert survey.** Six pairwise factor comparisons (four factors: 4 × 3 ÷ 2) on the Saaty 1–9 scale,
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
next-month returns, and its risk-based sizing does not meaningfully reduce drawdown.**
Both halves of the product were tested against pass marks fixed in advance, and
both fell short. We state this in the report, in the code, and in the product
itself.

We regard this as the project's strength. The contribution is not a profitable
screener but a **demonstrated method for finding out**, comprising:

1. Point-in-time evaluation with no look-ahead
2. A luck bar controlling for random selection, not merely for the market
3. An information-coefficient test of whether scores carry information at all
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
$PY backtest.py         # IC + luck bar   -> reports/backtest.md
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
| Aggressive +10.1% vs +7.5% (team weights, 21 Sep) and +12.9% vs +8.6% (AHP weights, 7 Nov), 100% luck bar | The same contaminated 2016–2026 window; the sealed test refused this result |
| Aggressive +205% gross over 10 years (AHP weights, `backtest_costs.py`) | Survivor-only sample, contaminated decade |

**Safe to quote:** the information coefficient, blind-test luck bars and verdicts, the
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
