# Cost stress test - does the edge survive trading costs?

*Run 2026-11-07 21:30 &middot; took 6s &middot; reproduce with `python backtest_costs.py`*

## Parameters

- **rebalance**: yearly per profile
- **costs**: Thai round-trip
- **reports**: gross vs net + turnover

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching MAX monthly...

Last 10 yearly rebalances · buy&hold(10y) = +94%

profile       avg turnover  gross 10y     net@0.5%     net@1.0%
conservative          62%        74%          69%          65%
balanced              65%        70%          65%          60%
aggressive            71%       205%         195%         186%

(turnover = % of the book swapped each year · momentum trades most · survivorship-biased, read relatively)
```
