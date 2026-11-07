# Profile comparison - do the 3 risk profiles actually differ?

*Run 2026-11-07 21:30 &middot; took 25s &middot; reproduce with `python backtest_profiles.py`*

## Parameters

- **rebalance**: 12-month hold, point-in-time
- **measures**: return AND realized volatility

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

fair test: BUY the top picks, HOLD 12 months  (73 start-points)
buy & hold proxy (equal-weight, rebalanced monthly): +8.6% avg

profile        avg 12mo ret avg risk(vol) ret/risk   vs B&H  luck bar
conservative           7.1%         13.4%     0.53    -1.5       6%
balanced               7.5%         14.2%     0.53    -1.1      11%
aggressive            12.9%         16.2%     0.80    +4.3     100%

read: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk
```
