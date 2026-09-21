# 📖 SETScout — How It Works (the detailed version)

*Read [`../START-HERE.md`](../START-HERE.md) first for the 5-minute overview. This is the deep version — still
plain-language, just more of it. Every technical term is explained the first time it appears.*

---

## 1. What SETScout is (and is not)

SETScout is an **Explainable Investment Decision Support System (EIDSS)** for the Thai stock market. It answers:

> **"Which stocks should I spend time researching today, and how risky are they?"**

It does **NOT** answer "what will the price be" or "should I buy." That distinction is the heart of the project:

- ✅ **Discovery** — surfaces stocks worth a look, out of a big list nobody has time to read.
- ✅ **Risk** — attaches a plain-language risk number to every pick.
- ✅ **Explanation** — says *why*, in sentences a beginner understands.
- ❌ **Not prediction** — it doesn't forecast prices.
- ❌ **Not advice** — educational only, with disclaimers everywhere.

---

## 2. The pipeline, step by step

```
COLLECT → SCORE (the filter) → 3 ENGINES → today.json → WEBSITE
```

**① Collect.** Every run, we download ~2 years of daily prices for 95 SET100 stocks from Yahoo Finance
(`yfinance`). Free, real data.

**② Score (the "filter").** For each stock we compute **4 factors** (below), turn them into fair scores, and rank.
This is the core "screener."

**③ 3 engines.** The same 4 factors are combined with **three different weightings** — one per risk appetite
(conservative / balanced / aggressive). Each produces its own ranked list.

**④ today.json.** All three lists are written to one file. The engine runs **ahead of time** (batch precompute),
so the website never has to wait or compute anything live.

**⑤ Website.** `index.html` reads `today.json` and shows each stock as 4 plain sentences. The risk quiz decides
which engine's list you see.

> **Why precompute?** So users get instant results, and so the team can build the website and the engine
> *independently* — they only agree on the *shape* of `today.json` (a "data contract").

---

## 3. The 4 factors (what the score is made of)

Each is computed from **price history** (v1 uses price-based proxies; real fundamentals like P/E are the v2 upgrade):

| Factor | Plain meaning | How |
|---|---|---|
| 📈 **Momentum** | Is it going up lately? | 6-month return |
| 🏭 **ROE** | Does it earn well on its capital? | net profit ÷ average shareholders' equity, from the filed accounts |
| 🛡️ **Quality** | Is it calm, not wild? | low volatility |
| ❤️ **Health** | Does it survive bad markets? | small max-drawdown |

**Two important fairness steps:**
- **z-score** — each factor is put on a common scale centred at 0 (so "momentum" and "volatility", which have
  different units, can be added together fairly).
- **sector-neutralize** — a stock is scored against **its own sector peers**, not the whole market. Without this,
  one naturally-calm sector (banks) would sweep the top just for being calm. This fixed a real bias.

The **final score** = a weighted sum of the sector-adjusted factors, turned into a 0–100 percentile.
On the site this is shown as a plain **rank out of the universe** — "#7 / 95" — because a position on a
list needs no explanation, while "0.93" invites one. The rank is always computed against **every** scored
stock; filtering to one sector does not renumber the survivors.
Verdict bands: **top ~20% = Worth a look 🟢**, next chunk = Wait 🟡, rest = Not now 🔴.

---

## 4. The 3 engines (personalization = a recommender system)

Same factors, different weights. Your **risk quiz** answer picks the engine — this is a **personalized
recommender**: user profile → matching model.

| Engine | Weights (biggest first) | Character |
|---|---|---|
| 🛡️ **Conservative** | quality 50 · health 38 · mom 6 · ROE 6 | calm, lower-risk names |
| ⚖️ **Balanced** | quality 37 · mom 26 · health 21 · ROE 16 | the middle default |
| 🚀 **Aggressive** | mom 47 · ROE 35 · quality 12 · health 6 | bold, high-momentum names |

> The weights are **placeholders** for now. They'll be replaced by real numbers from the **AHP expert survey**
> (see `research/expert-ahp.md`) — that's how our primary data feeds the model.

---

## 5. The honest findings (from real backtests)

We tested the engines the way people actually use them: **buy the top picks, hold ~1 year**.

| Engine | Return (12mo) | vs Buy-and-Hold | Beats random |
|---|---|---|---|
| 🛡️ Conservative | +1.9% | −5.6 pts | 0% |
| ⚖️ Balanced | +3.2% | −4.3 pts | 0% |
| 🚀 Aggressive | **+8.4%** | **+0.9 pts** | 82% |

*(Re-measured 16 Sep 2026 on the engine with ROE, against a buy-and-hold average
of +7.5%. The earlier five-factor run read +1.3 / +1.9 / +9.0 with a 96% luck bar
for aggressive.)*

**How to read this honestly:**
- The **defensive engines don't beat the market.** That's *expected* (efficient markets say you can't reliably
  beat it with price patterns) — and it's **our thesis, not a bug.** Underperforming buy-and-hold puts us in the
  same boat as most professional funds.
- The **aggressive engine looked like an edge, and then did not survive a fair test.** On this window it edges
  buy-and-hold by 0.9 points and beats 82% of random portfolios — under the 90% bar we set in advance. When the
  same hypothesis was taken to a period we had never examined (`blind_test.py`, one shot, pass mark written
  first), it reached **81%** and beat buy-and-hold in only **2 of 5** three-year blocks. Its advantage on costs
  is real arithmetic but says nothing about whether the advantage exists: **do not describe this as an edge.**

**Caveats we keep out loud (honesty is the brand):**
- Long-history returns suffer **survivorship bias** (we only have today's survivors) — so we report the *relative*
  pattern, not the giant absolute numbers.
- **Momentum can crash** hard in reversals.
- One market, one period — not a promise.

---

## 6. The honesty rails (why this is credible)

These are the tools that separate real signal from luck — and they're what makes the project trustworthy:

- **Luck bar** — we compare the strategy against hundreds of *random* portfolios. Real skill beats most of them;
  luck doesn't. (The aggressive engine beat 82% of random — under our 90% pass mark; the defensive ones beat 0%.)
- **Calibration** — we checked: does a higher score actually mean a higher chance of going up? **It doesn't** —
  every score band went up ~47% of the time, a flat line (trend test p = 0.53). So the app shows **no hit-rate
  figure at all**: one that says the same thing about every stock only looks like a forecast. *We rank
  research-worthiness, we do NOT predict short-term direction.* The measurement itself lives in
  `reports/backtest.md`, as a finding.
- **No look-ahead** — every backtest scores using only past data, then measures the future. No cheating.
- **Educational, not advice** — soft wording, disclaimers, non-commercial.

> **Where did `p_win` go?** It was an invented formula (`0.44 + 0.22 × score`, shown as "Hit rate 66%") until
> 31 Aug 2026, then the **measured** figure, which turned out to be flat at ~47% across every score band over
> 83 complete months. A number that is the same for every stock but rendered per stock invites exactly the
> reading it cannot support, so on **16 Sep 2026** it was removed from the product altogether. The finding
> stays in the report; the field is gone from `today.json`.

---

## 7. What's real vs. still to build

**✅ Real now:** the scores, the verdicts, the risk numbers (VaR), the prices, the 3 engines, the backtests
(luck bar, calibration, hold-returns, costs), and **ROE for all 95 stocks** — 1,583 stock-years read from
annual filings in SEC Thailand's archive (2001–2026), three more from SET's own statements, and a quality
gate that withholds 16 values the data itself contradicts. Checked against SET's figures for the same
fiscal years: median gap 0.002 points over 282 stock-years.

**🔨 Still to build:**
- **AHP survey** → real factor weights (replaces the placeholders). *Primary data — start early, it has lead time.*
- **Investor survey** → validates the problem (also primary data).
- **More fundamentals** — ROE landed on 16 Sep 2026; P/E and earnings growth are the obvious next two,
  so that more than one of the four factors comes from the accounts.

---

## 8. How to run it (any PC with Python)

```bash
pip install pandas numpy yfinance      # one-time setup

cd engine                # all the Python + data lives here
python run_today.py      # refresh picks → writes today.json (all 3 engines)
python backtest.py       # the honesty check → luck bar + the up-rate table
```
Then open `app/index.html` in a browser. **AI rule for the team:** you may use AI to draft code, but you must be able
to **explain every line you commit** — Q&A day is merciless.

---

## 9. Mini-glossary

| Term | Plain meaning |
|---|---|
| **Factor** | one input signal (momentum, quality, …) |
| **z-score** | rescale so different factors can be compared/added fairly |
| **Sector-neutral** | judge a stock vs its own sector, not the whole market |
| **VaR** | "a normal-bad month could lose about X%" |
| **Buy-and-hold** | just buying and doing nothing — the bar to beat |
| **Momentum premium** | the documented tendency of recent winners to keep winning (for a while) |
| **Survivorship bias** | old data only has today's survivors → looks better than reality |
| **Luck bar** | % of random portfolios our strategy beats (skill vs luck) |
| **Calibration** | does "60% chance" actually happen 60% of the time? |
| **`today.json`** | the file the engine writes and the website reads (the data contract) |

---

*SETScout · Explainable Investment Decision Support · SET100 · For education & research only — not a buy/sell
recommendation · past performance ≠ future results.*
