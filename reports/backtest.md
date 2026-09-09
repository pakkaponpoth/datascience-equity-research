# Monthly rotation backtest - the honesty check

*Run 2026-08-31 19:28 &middot; took 26s &middot; reproduce with `python backtest.py`*

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
months tested: 84  (2019-08-31 -> 2026-08-31)
strategy total: +13.1%   (CAGR +1.8%)
buy & hold    : +44.0%   (CAGR +5.3%)
vs B&H        : -30.8 pts   -> trails buy & hold
monthly win-rate: 58%   Sharpe(annual): 0.19
LUCK BAR: beat 11% of 300 random portfolios (random median +39.0%)  -> within luck - not proven

=== p_win calibration (score decile -> actual up-rate) ===
  score  0-10 : won   46%   (n=703)
  score 10-20 : won   50%   (n=730)
  score 20-30 : won   48%   (n=738)
  score 30-40 : won   46%   (n=735)
  score 40-50 : won   49%   (n=725)
  score 50-60 : won   48%   (n=767)
  score 60-70 : won   48%   (n=741)
  score 70-80 : won   45%   (n=732)
  score 80-90 : won   47%   (n=736)
  score 90-100: won   44%   (n=791)

wrote calibration.json  (run_today.py can read this for a REAL p_win)
```
