# Profile comparison - do the 3 risk profiles actually differ?

*Run 2026-08-31 19:29 &middot; took 20s &middot; reproduce with `python backtest_profiles.py`*

## Parameters

- **rebalance**: 12-month hold, point-in-time
- **measures**: return AND realized volatility

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

fair test: BUY the top picks, HOLD 12 months  (73 start-points)
buy & hold (whole universe): +7.0% avg

profile        avg 12mo ret avg risk(vol) ret/risk   vs B&H  luck bar
conservative           1.2%         15.1%     0.08    -5.8       0%
balanced               1.7%         15.2%     0.11    -5.4       0%
aggressive             8.8%         17.1%     0.51    +1.8      96%

read: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk
```
