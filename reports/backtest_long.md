# Long-horizon backtest - 5y and 10y per profile

*Run 2026-09-21 22:27 &middot; took 6s &middot; reproduce with `python backtest_long.py`*

## Parameters

- **rebalance**: yearly, top 20% per profile
- **horizons**: 5y, 10y, full window
- **caveat**: universe = today's survivors, so old returns are inflated

## Output

```
universe: 95 tickers from universe.json
95 tickers - fetching MAX monthly history...
history: 1988-08-01 -> 2026-09-01 (458 months)

25 yearly rebalances: 2001-08-01 -> 2025-08-01

profile          last 5y   last 10y      full     CAGR
conservative         40%        60%    18914%   +23.4%
balanced             40%        46%    26480%   +25.0%
aggressive           18%       126%    22919%   +24.3%
buy & hold           12%        94%    12796%   +21.5%

(cumulative % over the window · CAGR = annual growth rate · survivorship-biased)
```
