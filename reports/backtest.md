# Monthly rotation backtest - the honesty check

*Run 2026-11-07 21:29 &middot; took 29s &middot; reproduce with `python backtest.py`*

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
months tested: 83  (2019-11-30 -> 2026-10-31)
strategy total: +15.7%   (CAGR +2.1%)
buy & hold    : +44.0%   (CAGR +5.4%)
vs B&H        : -28.3 pts   -> trails buy & hold
monthly win-rate: 53%   Sharpe(annual): 0.21
LUCK BAR: beat 13% of 300 random portfolios (random median +39.0%)  -> within luck - not proven

=== up-rate by score band (a finding - nothing reads this at runtime) ===
  score  0-10 : won 47.1%   (n=699)
  score 10-20 : won 48.3%   (n=724)
  score 20-30 : won 48.1%   (n=732)
  score 30-40 : won 49.5%   (n=729)
  score 40-50 : won 46.0%   (n=721)
  score 50-60 : won 44.5%   (n=761)
  score 60-70 : won 44.5%   (n=737)
  score 70-80 : won 49.0%   (n=726)
  score 80-90 : won 46.0%   (n=732)
  score 90-100: won 48.5%   (n=786)

  flat at 47.2% across 10 bands, spread 5.0pp over 83 months, n = 7347 stock-months
  trend from low scores to high (Cochran-Armitage): z = -0.43, p = 0.66  -> NO trend
  any difference at all (chi-square): 8.8 on df 9, below the 5% critical value 16.919
  -> the score does not predict direction. No p_win is published.

=== information coefficient (83 months) ===
  mean rank correlation, score vs next-month return: +0.0128
  t = +0.54   ·   positive in 49/83 months (59%)   ·   month-to-month sd 0.215
  a useful equity signal runs 0.03-0.05. Ours is an order of magnitude
  below that and statistically indistinguishable from zero, which is the
  same finding as the flat up-rate, reached from the ordering side.
```
