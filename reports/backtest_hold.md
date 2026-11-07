# Hold test - buy the picks and hold (the fair test)

*Run 2026-11-07 21:29 &middot; took 38s &middot; reproduce with `python backtest_hold.py`*

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
picks avg 6-mo return : +3.7%
buy & hold avg          : +4.9%
vs B&H                  : -1.2 pts  -> trails
picks up after 6mo     : 59%
LUCK BAR: beat 4% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 50%  54%  51%  51%  53%

=== HOLD 12 months  (73 start-points) ===
picks avg 12-mo return : +7.7%
buy & hold avg          : +9.8%
vs B&H                  : -2.1 pts  -> trails
picks up after 12mo     : 60%
LUCK BAR: beat 3% of 300 random books  -> within luck
  up-rate by score quintile (low->high): 50%  52%  50%  47%  55%
```
