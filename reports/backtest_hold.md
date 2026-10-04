# Hold test - buy the picks and hold (the fair test)

*Run 2026-09-21 22:26 &middot; took 41s &middot; reproduce with `python backtest_hold.py`*

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
picks avg 6-mo return : +2.4%
buy & hold avg          : +3.9%
vs B&H                  : -1.5 pts  -> trails
picks up after 6mo     : 52%
LUCK BAR: beat 1% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 50%  52%  49%  48%  51%

=== HOLD 12 months  (73 start-points) ===
picks avg 12-mo return : +5.9%
buy & hold avg          : +8.8%
vs B&H                  : -2.8 pts  -> trails
picks up after 12mo     : 56%
LUCK BAR: beat 2% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 50%  50%  49%  45%  53%
```
