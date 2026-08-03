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

**① Collect.** Every run, we download ~2 years of daily prices for ~92 SET100 stocks from Yahoo Finance
(`yfinance`). Free, real data.

**② Score (the "filter").** For each stock we compute **5 factors** (below), turn them into fair scores, and rank.
This is the core "screener."

**③ 3 engines.** The same 5 factors are combined with **three different weightings** — one per risk appetite
(conservative / balanced / aggressive). Each produces its own ranked list.

**④ today.json.** All three lists are written to one file. The engine runs **ahead of time** (batch precompute),
so the website never has to wait or compute anything live.

**⑤ Website.** `index.html` reads `today.json` and shows each stock as 4 plain sentences. The risk quiz decides
which engine's list you see.

> **Why precompute?** So users get instant results, and so the team can build the website and the engine
> *independently* — they only agree on the *shape* of `today.json` (a "data contract").

---

## 3. The 5 factors (what the score is made of)

Each is computed from **price history** (v1 uses price-based proxies; real fundamentals like P/E are the v2 upgrade):

| Factor | Plain meaning | How |
|---|---|---|
| 📈 **Momentum** | Is it going up lately? | 6-month return |
| 🌱 **Growth** | Longer up-trend? | 12-month return |
| ⚖️ **Value** | Is it "cheap" vs itself? | price below its own 200-day average (mean-reversion) |
| 🛡️ **Quality** | Is it calm, not wild? | low volatility |
| ❤️ **Health** | Does it survive bad markets? | small max-drawdown |

**Two important fairness steps:**
- **z-score** — each factor is put on a common scale centred at 0 (so "momentum" and "volatility", which have
  different units, can be added together fairly).
- **sector-neutralize** — a stock is scored against **its own sector peers**, not the whole market. Without this,
  one naturally-calm sector (banks) would sweep the top just for being calm. This fixed a real bias.

The **final score** = a weighted sum of the sector-adjusted factors, turned into a 0–100 percentile.
Verdict bands: **top ~20% = Worth a look 🟢**, next chunk = Wait 🟡, rest = Not now 🔴.

---

## 4. The 3 engines (personalization = a recommender system)

Same factors, different weights. Your **risk quiz** answer picks the engine — this is a **personalized
recommender**: user profile → matching model.

| Engine | Weights (biggest first) | Character |
|---|---|---|
| 🛡️ **Conservative** | quality 40 · health 30 · value 20 · mom 5 · growth 5 | calm, lower-risk names |
| ⚖️ **Balanced** | quality 28 · value 24 · mom 20 · health 16 · growth 12 | the middle default |
| 🚀 **Aggressive** | mom 40 · growth 30 · value 15 · quality 10 · health 5 | bold, high-momentum names |

> The weights are **placeholders** for now. They'll be replaced by real numbers from the **AHP expert survey**
> (see `research/expert-ahp.md`) — that's how our primary data feeds the model.

---

## 5. The honest findings (from real backtests)

We tested the engines the way people actually use them: **buy the top picks, hold ~1 year**.

| Engine | Return (12mo) | vs Buy-and-Hold | Beats random |
|---|---|---|---|
| 🛡️ Conservative | +1.3% | −5.4 pts | 0% |
| ⚖️ Balanced | +1.9% | −4.8 pts | 0% |
| 🚀 Aggressive | **+9.0%** | **+2.3 pts** | **96%** |

**How to read this honestly:**
- The **defensive engines don't beat the market.** That's *expected* (efficient markets say you can't reliably
  beat it with price patterns) — and it's **our thesis, not a bug.** Underperforming buy-and-hold puts us in the
  same boat as most professional funds.
- The **aggressive engine does show a real edge** — this is the well-documented **momentum premium**. And it
  **survives trading costs**: +126% net over 10 years vs +86% for buy-and-hold, even at a pessimistic 1% round-trip fee.

**Caveats we keep out loud (honesty is the brand):**
- Long-history returns suffer **survivorship bias** (we only have today's survivors) — so we report the *relative*
  pattern, not the giant absolute numbers.
- **Momentum can crash** hard in reversals.
- One market, one period — not a promise.

---

## 6. The honesty rails (why this is credible)

These are the tools that separate real signal from luck — and they're what makes the project trustworthy:

- **Luck bar** — we compare the strategy against hundreds of *random* portfolios. Real skill beats most of them;
  luck doesn't. (The aggressive engine beat 96% of random; the defensive ones beat 0%.)
- **Calibration** (`calibration.json`) — we checked: does a higher score actually mean a higher chance of going
  up? **It doesn't** — every score bucket went up ~47% of the time (a flat line). So the honest **`p_win` ≈ 47%**
  for everything: *we rank research-worthiness, we do NOT predict short-term direction.*
- **No look-ahead** — every backtest scores using only past data, then measures the future. No cheating.
- **Educational, not advice** — soft wording, disclaimers, non-commercial.

> **What is `p_win`?** It's the "chance it works" number shown on each stock. Right now it's a placeholder
> formula; wiring it to `calibration.json` makes it the *real* (honest ~47%) number.

---

## 7. What's real vs. still to build

**✅ Real now:** the scores, the verdicts, the risk numbers (VaR), the prices, the 3 engines, and the backtests
(luck bar, calibration, hold-returns, costs).

**🔨 Still to build:**
- Wire `calibration.json` into `run_today.py` so `p_win` is the real ~47% (not the placeholder formula).
- **AHP survey** → real factor weights (replaces the placeholders). *Primary data — start early, it has lead time.*
- **Investor survey** → validates the problem (also primary data).
- **v2 fundamentals** — add P/E, ROE, earnings growth so factors aren't only price-based.

---

## 8. How to run it (any PC with Python)

```bash
pip install pandas numpy yfinance      # one-time setup

python run_today.py     # refresh picks → writes today.json (all 3 engines)
python backtest.py      # the honesty check → luck bar + writes calibration.json
```
Then open `index.html` in a browser. **AI rule for the team:** you may use AI to draft code, but you must be able
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
