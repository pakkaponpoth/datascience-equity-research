# Long-horizon backtest - 5y and 10y per profile

*Run 2026-08-31 19:30 &middot; took 5s &middot; reproduce with `python backtest_long.py`*

## Parameters

- **rebalance**: yearly, top 20% per profile
- **horizons**: 5y, 10y, full window
- **caveat**: universe = today's survivors, so old returns are inflated

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching MAX monthly history...
history: 1988-08-01 -> 2026-08-01 (457 months)

25 yearly rebalances: 2001-08-01 -> 2025-08-01

profile          last 5y   last 10y      full     CAGR
conservative        -10%        30%    16707%   +22.7%
balanced            -13%        22%    17636%   +23.0%
aggressive           24%       184%    27237%   +25.2%
buy & hold           12%        94%    12795%   +21.5%

(cumulative % over the window · CAGR = annual growth rate · survivorship-biased)
```
