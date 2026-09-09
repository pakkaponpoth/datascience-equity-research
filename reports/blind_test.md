# Blind test - frozen rule on a never-inspected period

*Run 2026-08-31 19:45 &middot; took 90s &middot; reproduce with `python blind_test.py`*

## Parameters

- **design**: pre-registered, one shot
- **sealed**: score 1999-01 to 2014-12, holds complete by 2015-12
- **development**: score 2016-01 to present (contaminated, shown for contrast)
- **frozen**: weights verbatim from run_today.py; top 20%; 12-month hold
- **decision rule**: REPLICATES = beats B&H and luck bar >= 90%

## Output

```
universe: 95 tickers from universe.json
fetching MAX monthly history...
history: 1988-08-31 -> 2026-08-31  (457 months)

==================================================================
SEALED PERIOD - the blind test. This is the evidence.
==================================================================

=== SEALED 1999-2014 (never inspected) ===
start-points: 168   (2001-01-31 -> 2014-12-31)
stocks with usable history: 37-62 (median 49 of 95)
buy & hold (equal weight, 12-month hold): +41.1% avg

profile         avg 12mo   vs B&H  luck bar               verdict
conservative       57.9%   +16.9      100%            REPLICATES
balanced           60.2%   +19.1      100%            REPLICATES
aggressive         44.1%    +3.0       81%                  WEAK

--- SEALED: non-overlapping 3-year blocks (robustness) ---
block             aggressive      B&H   beat?
2001-2003             101.4%    75.6%     yes
2004-2006              22.4%    36.8%      no
2007-2009              30.1%    31.4%      no
2010-2012              45.1%    39.1%     yes
2013-2015              10.1%    13.3%      no
beat buy-and-hold in 2/5 blocks (40%) - coin-flip expectation is 50%

==================================================================
DEVELOPMENT PERIOD - contaminated. Shown for contrast, NOT evidence.
==================================================================

=== DEVELOPMENT 2016-now (already examined ~15 times) ===
start-points: 116   (2016-01-31 -> 2025-08-31)
stocks with usable history: 66-92 (median 83 of 95)
buy & hold (equal weight, 12-month hold): +7.5% avg

profile         avg 12mo   vs B&H  luck bar               verdict
conservative        3.9%    -3.7        0%    DOES NOT REPLICATE
balanced            4.1%    -3.4        0%    DOES NOT REPLICATE
aggressive          7.7%    +0.2       56%                  WEAK

==================================================================
HOW TO READ THIS
==================================================================
The sealed result is the only one that carries evidential weight.
If sealed and development disagree, the development result was the
story we told ourselves after seeing the data - not a finding.
Sidak-corrected bar for a genuine 90% claim across 3 profiles: 96.6%.
Survivorship bias is NOT corrected: the universe is today's SET100,
so absolute levels are inflated in every arm. Compare, do not quote.
```
