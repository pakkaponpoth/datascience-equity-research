# Profile comparison - do the 3 risk profiles actually differ?

*Run 2026-09-09 13:44 &middot; took 21s &middot; reproduce with `python backtest_profiles.py`*

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
conservative           2.1%         14.8%     0.14    -5.4       0%
balanced               4.8%         15.3%     0.32    -2.7       0%
aggressive             9.6%         16.9%     0.56    +2.0      98%

read: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk
```
