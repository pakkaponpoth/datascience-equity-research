# Proposal A — The Honest Engine (standalone)
### "Which Stock Today?" — a recommender that tells the truth

_Pon's proposal, standalone version. One page. The integrated version
(combining with Q's SETscout) is proposal 02 — read that one second._

## The idea

A beginner asks *"which stock should I buy today?"* and gets a plain-language
answer **with the risk attached** — and the system is honest enough to
sometimes answer **"none today."** No fake price targets, no confident
guessing: every recommendation carries computed risk, ML-checked confidence,
and a **trust label** showing how the system scored in its own testing.

## The four things a user ever sees (the complexity firewall)

1. **Verdict** — "Looks good ✅ / Wait 🟡 / Not now 🔴"
2. **Risk sentence** — "A normal-bad month for this stock is about −16%.
   Of every 100 baht, put at most 23 here."
3. **Because sentence** — "Because the price is above its long average and
   hasn't just spiked." (generated from the model's own arithmetic)
4. **Trust label** — "Tested on 10 years of data. When we say 60%, it
   happened ~60% of the time. We don't promise profit — we tell you risk."

Everything more complicated stays inside the engine. That's a design rule.

## What's inside — eight jobs, explained like a normal person

1. **The data keeper.** Fetches every stock's price history, checks it isn't
   broken, and locks part of it in a sealed box we may not open until the
   very end — that box is how we prove we didn't cheat. Like keeping the
   answer key in a locked drawer while you study.
2. **The rule writer.** Two simple buying rules anyone can check by hand:
   "the price has been climbing — climb with it," and "the price dropped far
   below its usual level — it usually comes back." No black box; verify with
   a ruler on a chart.
3. **The time machine.** Replays the last ten years as if we had actually
   traded a rule — including broker fees on every trade. This is where most
   amateur systems die: ideas that trade too often get eaten alive by fees,
   and the time machine shows it mercilessly.
4. **The what-if machine.** Shuffles each stock's own past days and replays
   them thousands of times to see what *could* happen next month. Result:
   one honest sentence — "in a normal-bad month this loses about 16%" — and
   a rule of thumb: "so at most 23 of every 100 baht here."
5. **The second opinion** (our one ML piece, and it's humble). Before acting
   on a signal, it asks history: "when things looked like today, did this
   signal actually work?" If the answer is a coin flip, we don't act. The
   friend who says "are you sure?" before you press buy.
6. **The referee.** Re-runs the whole experiment across sixteen different
   time periods: does it keep working, or did it get lucky once? It even
   computes how good a totally *random* idea would look after our number of
   tries, so we can't fool ourselves. Most projects have no referee. Ours
   is the star.
7. **The translator.** Turns all of it into four sentences a first-timer can
   act on: verdict, risk in baht, the reason, and how much to trust us. If a
   sentence needs a finance dictionary, it gets rejected.
8. **The shop window.** The web page: pick a category (Thai blue chips, US
   tech, gold, whole world), see today's list, click a stock, read the four
   sentences. This owner also leads the report and presentation.

Note what's NOT here: seven of the eight layers are arithmetic, replay, and
honesty machinery — fully explainable by hand. Only layer 5 is AI at all,
and its whole job is to say "not sure enough."

## The Strategy Arena (everyone plays)

Every member writes ONE 10-line trading rule + a one-line story. The Arena
runs all rules through identical honest machinery (it does the anti-cheating
shift itself) and prints a leaderboard — with a luck-bar footer showing what
the best of N random ideas would score by chance. Most rules lose to
buy-and-hold; **that's the lesson, and each member presents their own.**

## Why it's a strong course project

Full DS lifecycle; supervised ML with honest metrics (AUC, precision,
calibration); a validation story most student teams can't tell (frozen
splits, walk-forward, luck-adjusted statistics); and a live demo — the daily
recommendation generates in five seconds on stage.
