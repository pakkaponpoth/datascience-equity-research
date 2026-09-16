# Profile comparison - do the 3 risk profiles actually differ?

*Run 2026-09-16 14:55 &middot; took 23s &middot; reproduce with `python backtest_profiles.py`*

## Parameters

- **rebalance**: 12-month hold, point-in-time
- **measures**: return AND realized volatility

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching ~8y monthly prices...

fair test: BUY the top picks, HOLD 12 months  (73 start-points)
buy & hold (whole universe): +7.5% avg

profile        avg 12mo ret avg risk(vol) ret/risk   vs B&H  luck bar
conservative           1.9%         14.9%     0.13    -5.6       0%
balanced               3.2%         15.8%     0.20    -4.3       0%
aggressive             8.4%         17.2%     0.48    +0.9      82%

read: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk
```
