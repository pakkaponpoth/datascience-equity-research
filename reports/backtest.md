# Monthly rotation backtest - the honesty check

*Run 2026-09-16 14:57 &middot; took 24s &middot; reproduce with `python backtest.py`*

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
strategy total: +14.4%   (CAGR +2.0%)
buy & hold    : +46.8%   (CAGR +5.7%)
vs B&H        : -32.5 pts   -> trails buy & hold
monthly win-rate: 55%   Sharpe(annual): 0.20
LUCK BAR: beat 8% of 300 random portfolios (random median +43.4%)  -> within luck - not proven

=== up-rate by score band (a finding - nothing reads this at runtime) ===
  score  0-10 : won 46.1%   (n=696)
  score 10-20 : won 48.9%   (n=722)
  score 20-30 : won 48.6%   (n=730)
  score 30-40 : won 48.1%   (n=727)
  score 40-50 : won 48.3%   (n=717)
  score 50-60 : won 46.9%   (n=759)
  score 60-70 : won 47.2%   (n=733)
  score 70-80 : won 45.7%   (n=724)
  score 80-90 : won 49.6%   (n=728)
  score 90-100: won 44.1%   (n=783)

  flat at 47.4% across 10 bands, spread 5.5pp over 83 months, n = 7319 stock-months
  trend from low scores to high (Cochran-Armitage): z = -1.04, p = 0.30  -> NO trend
  any difference at all (chi-square): 7.7 on df 9, below the 5% critical value 16.919
  -> the score does not predict direction. No p_win is published.
```
