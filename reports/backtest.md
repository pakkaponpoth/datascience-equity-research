# Monthly rotation backtest - the honesty check

*Run 2026-09-21 22:25 &middot; took 24s &middot; reproduce with `python backtest.py`*

## Parameters

- **rebalance**: monthly, buy top 20%
- **history**: ~8y monthly
- **luck bar**: 300 random portfolios
- **outputs**: the up-rate table below - a finding, not a runtime input

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

=== SETScout backtest ===
months tested: 83  (2019-09-30 -> 2026-08-31)
strategy total: +24.7%   (CAGR +3.2%)
buy & hold    : +46.8%   (CAGR +5.7%)
vs B&H        : -22.1 pts   -> trails buy & hold
monthly win-rate: 54%   Sharpe(annual): 0.28
LUCK BAR: beat 17% of 300 random portfolios (random median +43.4%)  -> within luck - not proven

=== up-rate by score band (a finding - nothing reads this at runtime) ===
  score  0-10 : won 47.7%   (n=696)
  score 10-20 : won 50.0%   (n=722)
  score 20-30 : won 49.2%   (n=730)
  score 30-40 : won 48.1%   (n=727)
  score 40-50 : won 47.4%   (n=717)
  score 50-60 : won 43.1%   (n=759)
  score 60-70 : won 45.0%   (n=733)
  score 70-80 : won 48.5%   (n=724)
  score 80-90 : won 46.0%   (n=728)
  score 90-100: won 48.5%   (n=783)

  flat at 47.4% across 10 bands, spread 6.9pp over 83 months, n = 7319 stock-months
  trend from low scores to high (Cochran-Armitage): z = -1.09, p = 0.28  -> NO trend
  any difference at all (chi-square): 11.7 on df 9, below the 5% critical value 16.919
  -> the score does not predict direction. No p_win is published.

=== information coefficient (83 months) ===
  mean rank correlation, score vs next-month return: +0.0050
  t = +0.20   ·   positive in 41/83 months (49%)   ·   month-to-month sd 0.233
  a useful equity signal runs 0.03-0.05. Ours is an order of magnitude
  below that and statistically indistinguishable from zero, which is the
  same finding as the flat up-rate, reached from the ordering side.
```
