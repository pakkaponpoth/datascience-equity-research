# Monthly rotation backtest - the honesty check

*Run 2026-09-13 01:45 &middot; took 25s &middot; reproduce with `python backtest.py`*

## Parameters

- **rebalance**: monthly, buy top 20%
- **history**: ~8y monthly
- **luck bar**: 300 random portfolios
- **outputs**: calibration.json (score decile -> real up-rate)

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

=== SETScout backtest ===
months tested: 83  (2019-09-30 -> 2026-08-31)
strategy total: +46.1%   (CAGR +5.6%)
buy & hold    : +46.8%   (CAGR +5.7%)
vs B&H        : -0.7 pts   -> trails buy & hold
monthly win-rate: 58%   Sharpe(annual): 0.40
LUCK BAR: beat 54% of 300 random portfolios (random median +43.4%)  -> within luck - not proven

=== p_win calibration (score decile -> actual up-rate) ===
  score  0-10 : won   44%   (n=696)
  score 10-20 : won   52%   (n=722)
  score 20-30 : won   47%   (n=730)
  score 30-40 : won   48%   (n=727)
  score 40-50 : won   47%   (n=717)
  score 50-60 : won   49%   (n=759)
  score 60-70 : won   48%   (n=733)
  score 70-80 : won   44%   (n=724)
  score 80-90 : won   47%   (n=728)
  score 90-100: won   47%   (n=783)

wrote calibration.json  (run_today.py can read this for a REAL p_win)
```
