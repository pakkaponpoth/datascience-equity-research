# 🚀 SETScout — quick status (Atlas working copy)
*(the 30-second version · full state = `CONTINUE.md` · full design = `HANDOFF.md`)*

**Live:** https://oksoimcodingnow.github.io/atlas/setscout/

## ✅ What we've done
- **Website** — SET100 · verdict **+ sector** filters · TH/EN · dark/light · **risk-quiz** personalization · **"ⓘ How we score"** panel · **💰 DCA** calculator
- **Engine** (`run_today.py`) — **de-biased** (z-score + sector-neutral) → no more bank cluster, spread across sectors, no ties
- **Backtest** (`backtest.py`) — luck bar + p_win calibration. **Honest finding: the strategy does NOT beat buy-and-hold** (that's the *thesis*, not a bug — don't fake an edge)
- **Synced to Pakkapon's repo** + `CONTINUE.md` written
- **Python now installed here** → can run engine + backtest end-to-end

## ▶️ Do FIRST (next session)
1. **Re-run backtest as "buy picks & HOLD ~1 year"** (matches how people actually use it, not monthly churn) — fairer + likely looks much better
2. **Wire real `p_win`** from `calibration.json` into `run_today.py` (replaces the placeholder ~0.44+score)
3. **AHP survey** — finalize `research/expert-ahp.md`, send to 6–10 experts (primary data · has lead time · start early)

## 🧭 Remember
SETScout = **discovery + risk + explanation**, *not* a beat-the-market system. The honest backtest is a **strength** for the report. Keep the "educational, not advice" disclaimer.

*(To run: `python run_today.py` / `python backtest.py` · setup: `pip install pandas numpy yfinance`)*
