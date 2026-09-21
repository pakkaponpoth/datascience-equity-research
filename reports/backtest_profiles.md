# Profile comparison - do the 3 risk profiles actually differ?

*Run 2026-09-21 22:26 &middot; took 23s &middot; reproduce with `python backtest_profiles.py`*

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
conservative           5.2%         13.7%     0.38    -2.3       0%
balanced               5.8%         14.5%     0.40    -1.8       4%
aggressive            10.1%         17.1%     0.59    +2.5     100%

read: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk
```
