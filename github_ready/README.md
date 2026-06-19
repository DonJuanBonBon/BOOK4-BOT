[README.md](https://github.com/user-attachments/files/29143893/README.md)
# Honest Quant Research Engine + Multi-Strategy Book

A start-to-finish, brutally honest attempt to build a trading strategy that beats simply buying and
holding the US stock market (SPY) — and a reusable engine that judges any trading idea fairly.

**Plain-English story of the whole project:** see `docs/PROJECT_SUMMARY_plain_english.md` (written for
someone who has never coded or traded).

## The honest bottom line (read this first)
After testing momentum, day-trading, multi-strategy combinations, and paid professional factor data, we
did **not** find a way to make more dollars than buying and holding SPY once realistic costs (trading
fees, short-borrow, and the cost of leverage) are charged. That is the truthful result — and most people
learn it by losing money instead of by careful testing. What this repo *does* give you:
1. A rigorous, reusable **honesty engine** that charges real costs, tests on unseen data, and compares to
   SPY before declaring anything a "win."
2. A diversified, **unlevered** portfolio that delivers roughly market-like returns with about half the
   drawdown (a calmer ride, not a money machine).
3. A full **logbook** (`docs/results_ledger.md`) of every test and its honest result.

## What's here
- `src/` — the engine and strategies (Python):
  - `indicators.py` — technical indicators, built from scratch and validated.
  - `edge_harness.py` — the "lie-detector": no-look-ahead backtester + the both-axes-vs-SPY gate.
  - `panel_strategies.py` — cross-sectional sleeves (momentum, residual momentum, low-vol, trend, value).
  - `multi_strategy_book_v2.py`, `book_with_value.py` — combine sleeves into a risk-balanced book.
  - `aqr_factor_book.py`, `build_value_quality.py`, `survivorship_free_momentum_v2.py`, `ls_residual_momentum.py` — research runs.
- `fetchers/` — scripts that download the market data (run on your own machine; they read API keys from
  environment variables and never store them).
- `docs/` — the plain-English summary, the research notes, the results, and the full test logbook.

## How to use it
1. `pip install -r requirements.txt`
2. Set any API keys as environment variables (never in a file):
   `setx ALPACA_API_KEY ...`, `setx EODHD_API_KEY ...`, `setx DATABENTO_API_KEY ...` (only the ones you use).
3. Run the relevant `fetchers/*.py` to download data into local folders (data is NOT included in this repo).
4. Point the `src/` scripts at your data folders and run them.

## Important
- **No data and no API keys are included** (see `.gitignore`). You supply your own.
- Keys live ONLY in environment variables. Never commit them.
- This is research/education, not investment advice. Past backtests do not predict future returns.

---

## How the bot actually works, step by step (for someone brand new to this)

Imagine a talent scout for a sports team. Every month, the scout looks at thousands of players, grades
each one on a few different qualities, drafts the best, drops the worst, and then checks how that team
did the *following* month. Our bot is that scout — but for stocks, replaying history one month at a time.
Here is exactly what it does each step.

### The setup: what data it reads
The bot is handed two things for thousands of companies, going back ~20 years:
1. **Prices** — what each stock closed at, month by month (including companies that later went bankrupt,
   so the test isn't cheating by only looking at survivors).
2. **Fundamentals** — basic company facts from their financial reports: how much the company is worth on
   paper (book value), its earnings, its profits, and its debt — each tagged with the date it was
   actually made public (so the bot can never "see" a report before it existed).

### What happens each month (the bot repeats this ~250 times, once per month)
**Step 1 — Freeze time.** The bot pretends it's standing on, say, March 2015. It is only allowed to use
information that existed on or before that day. This "no peeking at the future" rule is the single most
important honesty guard — break it and any strategy looks like a genius.

**Step 2 — Pick the playable universe.** Out of thousands of stocks, it keeps only the ~500 most heavily
traded ones priced above $5. Why: those are the ones you could actually buy and sell in real life without
moving the price or getting stuck. Penny stocks and ghosts are thrown out.

**Step 3 — Grade every stock on several independent "lenses."** Each lens is a different, well-known way
to spot an attractive stock. These grades are the "indicators":
- **Momentum** — how much the stock went up over the past ~12 months (skipping the most recent month,
  because very recent moves tend to reverse). Idea: winners tend to keep winning for a while.
- **Residual momentum** — the same idea, but first subtracting out how much the stock just moved *with the
  overall market*, leaving only its own personal strength. (We do this with a bit of math called a
  regression — think "removing the tide to see how well each boat is actually sailing.")
- **Low volatility** — how calm and steady the stock's price has been. Idea: surprisingly, calmer stocks
  have historically given better returns for the risk.
- **Value** — how *cheap* the stock is versus what the company is actually worth (its book value and its
  earnings). Idea: bargains tend to pay off. (This one needs the fundamentals data.)
- **Quality** — how profitable and financially safe the company is (good profits, low debt). (We tested
  this; it didn't earn its keep in our data, so it was dropped — honesty over wishful thinking.)
- **Trend** (a separate lens, run on commodities/bonds/currencies) — is the thing currently rising or
  falling, so you can ride it up or bet against it down.

**Step 4 — Build a mini-portfolio from each lens.** For each lens, the bot "buys" the top-graded stocks
and, for some lenses, "short sells" the worst (a short means you profit if it goes *down*). Each lens
becomes its own little team.

**Step 5 — Blend the teams so none bullies the others.** It combines the lenses so each contributes the
*same amount of risk* (this is called risk parity). A jumpy lens gets a smaller slice; a calm one gets a
bigger slice. The point: many different bets that don't move together = a smoother overall result.

**Step 6 — Place the trades for NEXT month, not today.** Crucially, the bot acts on its decisions using
the *following* month's prices — never the prices it just looked at. This mirrors real life (you can't buy
at a price that already happened) and is part of the no-peeking rule.

**Step 7 — Subtract real-world costs.** Every trade pays commissions and the spread; every short pays a
borrow fee; and if the strategy uses borrowed money (leverage), it pays interest. The bot deducts all of
this. (This step is what quietly kills most strategies — and it's exactly what deflated our best result.)

**Step 8 — Update the scoreboard.** It records the new running balance ($1,000 grows or shrinks), and
tracks the worst peak-to-bottom drop along the way.

### After replaying all ~20 years
The bot reports four things and stacks them against simply buying and holding the S&P 500 (SPY):
- **Total return** — what $1,000 turned into.
- **Worst drawdown** — the scariest drop you'd have had to stomach.
- **Sharpe ratio** — return earned per unit of nerve-racking bumpiness (higher = smoother for the gain).
- **The verdict** — did it beat SPY on *both* return and drawdown, in years it was never tuned on, after
  costs? Only then does it "pass."

### The two honesty checks built into every run
1. **Test on unseen years.** The bot designs on the first chunk of history and is graded on a later chunk
   it never saw — so we're measuring real skill, not memorization.
2. **Include the failures.** Bankrupt/delisted companies stay in the data, so the test can't flatter itself
   by only ever looking at the winners that happened to survive.

That's the whole machine: every month, grade thousands of stocks on a handful of time-tested lenses, blend
the bets so they balance, trade at next month's prices, pay real costs, and keep an honest scoreboard
against just owning the market — repeated across two decades.
