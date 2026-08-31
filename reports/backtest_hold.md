# Hold test - buy the picks and hold (the fair test)

*Run 2026-08-31 19:28 &middot; took 35s &middot; reproduce with `python backtest_hold.py`*

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
buy & hold avg          : +3.4%
vs B&H                  : -2.5 pts  -> trails
picks up after 6mo     : 57%
LUCK BAR: beat 0% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 49%  52%  49%  49%  47%

=== HOLD 12 months  (73 start-points) ===
picks avg 12-mo return : +1.5%
buy & hold avg          : +8.2%
vs B&H                  : -6.7 pts  -> trails
picks up after 12mo     : 52%
LUCK BAR: beat 0% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 49%  52%  50%  49%  45%
```
