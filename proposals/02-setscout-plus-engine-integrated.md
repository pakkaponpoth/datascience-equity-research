# Proposal B — SETscout + The Honest Engine (integrated)
### One pipeline: discover → analyze → trust

_The merge of Q's SETscout (discovery) and Pon's engine (risk/validation),
plus the Arena for all 8. This is the version proposed as THE project._

## Why these two ideas are halves of one system

| | Q's SETscout answers | Pon's engine answers |
|---|---|---|
| Question | *"Which companies should I spend time researching today?"* | *"If I look at this one — how risky is it, how much money, how much should I trust the answer?"* |
| Universe | wide (SET100 screening) | deep (per-stock analysis) |
| Data | fundamentals (PE/PBV, margins), technicals, news, macro | prices, signals, Monte Carlo risk, ML confidence |
| Output | ranked daily discovery list + LLM-written explanations | verdict, risk sentence, position size, trust label |

Neither replaces the other. A user flows through both:

```
  SETscout (discovery)                The Engine (analysis)
┌─────────────────────────┐        ┌──────────────────────────────┐
│ SET100 multi-factor     │ click  │ signals + Monte Carlo risk   │
│ screen: fundamental +   │ ─────► │ "normal-bad month −16%"      │
│ technical + news score  │  a     │ position size (risk budget)  │
│ → today's top-10 list   │ stock  │ ML-checked confidence        │
│ → LLM explains each     │        │ → verdict + trust label      │
└─────────────────────────┘        └──────────────────────────────┘
              ▼                                  ▼
        ┌──────────────────────────────────────────────┐
        │  THE REFEREE (validation — nobody else has it)│
        │  backtests w/ real costs · walk-forward ·     │
        │  luck-bar statistics · probability calibration│
        │  → the trust label printed on every page      │
        └──────────────────────────────────────────────┘
```

**The referee is the merge's superpower:** a discovery list is easy to build
and hard to trust. Our validation machinery is exactly what makes SETscout's
recommendations *defensible* in front of the professor — and the professor's
question "how do you know it works?" is the one every project dies on.

## What each proposal contributes (nothing is thrown away)

- **From SETscout:** the discovery framing (the product's front door), SET100
  breadth, fundamental features, news/qualitative layer (scoped: headlines
  for the top-N only), LLM-for-explanation-only, the dashboard.
- **From the engine:** honest backtesting with costs, Monte Carlo risk +
  position sizing, supervised ML with calibration, walk-forward + luck-bar
  validation, the newbie firewall (4 plain-language templates), worldwide
  extension (ETFs/gold/US tech as category cards), the trust label.
- **From everyone: the Strategy Arena** — each member authors one 10-line
  trading rule; identical machinery ranks all 8 on a leaderboard with a
  luck-bar footer. Personal stake for every member, zero prerequisite skill.

## Scope guards (so we actually finish)

1. News = **headlines for the top-10 discovered stocks only**, summarized by
   LLM. No full-article scraping pipelines.
2. Fundamentals = the ratios available from free sources (yfinance fields),
   ~6 ratios, not full statement parsing.
3. Storage = parquet/SQLite (same pipeline box, 5% of the pain of Postgres).
4. LLM writes explanations ONLY — never recommendations (Q's rule, kept).
5. Every scoring weight is stated once and not tuned — the referee counts
   every trial and the luck bar rises with each (that discipline is a
   feature we present, not bureaucracy).

## The 8 owners

| # | Layer | Half |
|---|---|---|
| 1 | Data pipeline: prices + fundamentals + FRED (collect/clean/store) | SETscout |
| 2 | Feature engineering: technical + fundamental scores | SETscout |
| 3 | News/qualitative: headlines + LLM explanation layer | SETscout |
| 4 | Discovery ranking + dashboard (the SETscout webapp) | SETscout |
| 5 | Risk engine: Monte Carlo, worst-month numbers, position sizing | Engine |
| 6 | Supervised ML + probability calibration (course ML requirement) | Engine |
| 7 | The referee: backtests, walk-forward, luck statistics, trust label | Engine |
| 8 | Newbie translator + story lead (report assembly, presentation arc) | shared |

**Plus: all 8 write one Arena rule each.** Presentation = the funnel in
order, ~90 seconds per person, live demo at the end (today's discovery list →
click a stock → the engine's verdict, generated on stage).

## Timeline (deadline 28 Aug)

- **Wk Jul 21:** roles claimed; SETscout data + scoring skeleton; engine
  layers already run — wired to accept SETscout's list.
- **Wk Jul 28:** discovery list v1 end-to-end; LLM explanations; Arena rules
  collected, first leaderboard.
- **Wk Aug 4–11:** dashboard polish; report per-role; live-diary week.
- **Aug 18–28:** rehearse, buffer, submit early.
