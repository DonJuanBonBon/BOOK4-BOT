#!/usr/bin/env python3
"""
fetch_intraday_alpaca.py  --  pull >=1 year of 15-minute (and daily) bars from Alpaca.
RUN THIS ON YOUR WINDOWS MACHINE (the sandbox can't reach Alpaca).

Keys are read from environment variables ONLY -- never hardcode them:
    setx ALPACA_API_KEY     "your_key"      (run once in a terminal, then reopen it)
    setx ALPACA_SECRET_KEY  "your_secret"
Free tier = IEX feed. IEX volume is a fraction of consolidated tape (understated) but is
internally consistent, so the strategy's relative-volume filter still works.

Install once:  pip install alpaca-py pandas
Run:           python fetch_intraday_alpaca.py
Output:        SYM_15m.csv and SYM_daily.csv in OUT_DIR, columns: datetime,open,high,low,close,volume
               datetime is naive US/Eastern, regular trading hours only (09:30-16:00 ET).
"""
from __future__ import annotations
import os, sys, time
from datetime import datetime, timedelta, timezone

# ---------------- CONFIG ----------------
LOOKBACK_DAYS = 400          # >1 year of calendar days (≈252 trading days after RTH filter)
OUT_DIR       = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "ClaudeAlgo")
INTRADAY_TF   = (15, "Minute")   # change to (1,"Hour") or (5,"Minute") if you want
FETCH_DAILY   = True             # also pull daily bars (needed for the EMA200 macro filter)
# A liquid, sector-diversified large-cap universe (still survivorship-biased: all trade today).
UNIVERSE = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","TSLA",        # mega tech
    "JPM","BAC","GS","V","MA",                                       # financials
    "UNH","JNJ","LLY","PFE",                                         # healthcare
    "XOM","CVX",                                                     # energy
    "WMT","COST","HD","NKE","MCD","KO","PG",                         # consumer
    "CAT","BA","HON",                                                # industrials
    "SPY","QQQ",                                                     # index ETFs (benchmarks)
]
RTH_START, RTH_END = "09:30", "16:00"
# ----------------------------------------

def die(msg):
    print(f"\nERROR: {msg}"); sys.exit(1)

try:
    import pandas as pd
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from alpaca.data.enums import Adjustment, DataFeed
except ImportError as e:
    die(f"missing package ({e}). Run:  pip install alpaca-py pandas")

KEY = os.environ.get("ALPACA_API_KEY")
SEC = os.environ.get("ALPACA_SECRET_KEY")
if not KEY or not SEC:
    die("ALPACA_API_KEY / ALPACA_SECRET_KEY not found in environment. Set them with setx and reopen the terminal.")

os.makedirs(OUT_DIR, exist_ok=True)
client = StockHistoricalDataClient(KEY, SEC)
unit = {"Minute": TimeFrameUnit.Minute, "Hour": TimeFrameUnit.Hour, "Day": TimeFrameUnit.Day}[INTRADAY_TF[1]]
tf_intraday = TimeFrame(INTRADAY_TF[0], unit)
tf_label = f"{INTRADAY_TF[0]}{'m' if INTRADAY_TF[1]=='Minute' else 'h'}"

start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
end   = datetime.now(timezone.utc) - timedelta(minutes=20)   # free feed: stay >15 min behind realtime

def fetch(symbol, timeframe):
    """Single call; alpaca-py auto-paginates the full range. Retry a few times on transient errors."""
    for attempt in range(4):
        try:
            req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=timeframe,
                                   start=start, end=end,
                                   adjustment=Adjustment.ALL, feed=DataFeed.IEX)
            bars = client.get_stock_bars(req)
            df = bars.df
            if df is None or len(df) == 0:
                return pd.DataFrame()
            df = df.reset_index()           # columns: symbol, timestamp, open, high, low, close, volume, ...
            return df
        except Exception as e:
            if attempt == 3:
                print(f"   {symbol}: FAILED after retries ({type(e).__name__}: {str(e)[:120]})")
                return None
            time.sleep(2 * (attempt + 1))

def to_et_rth(df, rth=True):
    ts = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("America/New_York")
    out = pd.DataFrame({
        "datetime": ts.dt.tz_localize(None),
        "open": df["open"].astype(float), "high": df["high"].astype(float),
        "low": df["low"].astype(float),  "close": df["close"].astype(float),
        "volume": df["volume"].astype(float),
    }).sort_values("datetime")
    if rth:
        t = out["datetime"].dt.strftime("%H:%M")
        out = out[(t >= RTH_START) & (t < RTH_END)]
    return out.reset_index(drop=True)

print(f"Fetching {tf_label} bars for {len(UNIVERSE)} symbols, {start.date()} -> {end.date()}  (feed=IEX, adj=ALL)")
print(f"Output dir: {OUT_DIR}\n")
report = []
for i, sym in enumerate(UNIVERSE, 1):
    raw = fetch(sym, tf_intraday)
    if raw is None: report.append((sym, "FAIL", "", "")); continue
    if len(raw) == 0: report.append((sym, "EMPTY", "", "")); print(f"[{i}/{len(UNIVERSE)}] {sym}: no data"); continue
    intr = to_et_rth(raw, rth=True)
    intr.to_csv(os.path.join(OUT_DIR, f"{sym}_{tf_label}.csv"), index=False)
    tdays = intr["datetime"].dt.normalize().nunique()
    report.append((sym, len(intr), f"{intr.datetime.min()} -> {intr.datetime.max()}", f"{tdays} td"))
    print(f"[{i}/{len(UNIVERSE)}] {sym}: {len(intr)} {tf_label} bars, {tdays} trading days")
    if FETCH_DAILY:
        draw = fetch(sym, TimeFrame(1, TimeFrameUnit.Day))
        if draw is not None and len(draw):
            daily = to_et_rth(draw, rth=False)
            daily["datetime"] = daily["datetime"].dt.normalize()
            daily.to_csv(os.path.join(OUT_DIR, f"{sym}_daily.csv"), index=False)
    time.sleep(0.3)   # gentle on the 200 req/min free limit

print("\n================ COVERAGE REPORT ================")
ok = [r for r in report if isinstance(r[1], int)]
print(f"Succeeded: {len(ok)}/{len(UNIVERSE)} symbols")
for sym, n, span, td in report:
    print(f"  {sym:6s} {str(n):>7}  {span}  {td}")
if ok:
    min_td = min(int(r[3].split()[0]) for r in ok)
    print(f"\nMin trading-day coverage across succeeded symbols: {min_td} days "
          f"({'OK: >1yr' if min_td >= 240 else 'WARNING: <1yr -- raise LOOKBACK_DAYS'})")
print("Done. CSVs saved to OUT_DIR. Tell Claude when the files are in ClaudeAlgo and we'll re-run the backtest.")
