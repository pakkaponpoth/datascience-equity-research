# Does risk-based sizing help? - pre-registered, one shot

*Run 2026-09-01 02:06 &middot; took 29s &middot; reproduce with `python backtest_sizing.py`*

## Parameters

- **hypothesis**: risk-cap weighting lowers max drawdown vs equal weight
- **construction**: weight = cap / sum(caps), fully invested
- **primary window**: 2016-01 to present (sizing never examined before)
- **criterion**: drawdown improves >= 20% at <= 2.0 pts return cost
- **note**: judged on RISK, not return

## Output

```
universe: 95 tickers from universe.json
fetching MAX monthly history...
history: 1988-08-31 -> 2026-08-31  (457 months)

======================================================================
PRIMARY  2016-now   (127 monthly rebalances)   <-- PRIMARY
======================================================================
profile       arm               maxDD  ann vol  ann ret  DD change  ret cost
conservative  equal weight     -38.5%    15.3%     3.7%
              risk-weighted    -39.0%    15.1%     3.2%      -1.1%     +0.5
                            verdict: NOT SUPPORTED
balanced      equal weight     -36.0%    15.5%     5.1%
              risk-weighted    -36.1%    15.1%     4.8%      -0.2%     +0.3
                            verdict: NOT SUPPORTED
aggressive    equal weight     -38.5%    17.5%    12.1%
              risk-weighted    -36.5%    16.5%    10.1%       5.1%     +2.0
                            verdict: NOT SUPPORTED

======================================================================
ROBUSTNESS  1999-2014   (168 monthly rebalances)   (robustness only)
======================================================================
profile       arm               maxDD  ann vol  ann ret  DD change  ret cost
conservative  equal weight     -49.8%    62.5%    41.6%
              risk-weighted    -49.5%    74.3%    43.7%       0.5%     -2.1
balanced      equal weight     -52.0%    63.0%    46.1%
              risk-weighted    -51.3%    76.2%    46.5%       1.3%     -0.4
aggressive    equal weight     -47.4%    27.6%    34.8%
              risk-weighted    -47.4%    26.5%    33.4%      -0.0%     +1.4

======================================================================
Pass mark was fixed before this ran: drawdown must improve >= 20%
at a return cost <= 2.0 points. Both arms hold the SAME stocks and
differ only in weights, so the comparison is internal - but the
universe is survivorship-biased, so do not quote absolute levels.
```
