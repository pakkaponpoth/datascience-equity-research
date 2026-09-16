# Hold test - buy the picks and hold (the fair test)

*Run 2026-09-16 14:58 &middot; took 38s &middot; reproduce with `python backtest_hold.py`*

## Parameters

- **rebalance**: none - buy and hold
- **horizons**: 6 and 12 months
- **history**: ~8y monthly
- **why**: matches how users actually behave, not monthly churn

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

=== HOLD 6 months  (79 start-points) ===
picks avg 6-mo return : +0.8%
buy & hold avg          : +3.9%
vs B&H                  : -3.1 pts  -> trails
picks up after 6mo     : 53%
LUCK BAR: beat 0% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 48%  53%  52%  50%  46%

=== HOLD 12 months  (73 start-points) ===
picks avg 12-mo return : +2.8%
buy & hold avg          : +8.7%
vs B&H                  : -5.9 pts  -> trails
picks up after 12mo     : 53%
LUCK BAR: beat 0% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 47%  53%  52%  48%  47%
```
