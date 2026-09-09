# Hold test - buy the picks and hold (the fair test)

*Run 2026-09-09 13:32 &middot; took 37s &middot; reproduce with `python backtest_hold.py`*

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
picks avg 6-mo return : +2.5%
buy & hold avg          : +3.9%
vs B&H                  : -1.4 pts  -> trails
picks up after 6mo     : 61%
LUCK BAR: beat 2% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 49%  53%  49%  51%  48%

=== HOLD 12 months  (73 start-points) ===
picks avg 12-mo return : +4.5%
buy & hold avg          : +8.8%
vs B&H                  : -4.3 pts  -> trails
picks up after 12mo     : 59%
LUCK BAR: beat 0% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 47%  54%  48%  50%  48%
```
