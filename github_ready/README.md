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
