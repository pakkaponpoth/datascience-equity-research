# Cost stress test - does the edge survive trading costs?

*Run 2026-09-21 22:27 &middot; took 7s &middot; reproduce with `python backtest_costs.py`*

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
conservative          56%        60%          56%          52%
balanced              64%        46%          42%          37%
aggressive            64%       126%         119%         113%

(turnover = % of the book swapped each year · momentum trades most · survivorship-biased, read relatively)
```
