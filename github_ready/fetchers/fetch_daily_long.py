#!/usr/bin/env python3
"""
fetch_daily_long.py -- pull 3 YEARS of DAILY bars so the 200-day trend filter is fully warm
before the intraday window. Daily bars are tiny, so this runs in seconds.
Run on this Windows machine:   python fetch_daily_long.py
Overwrites the short SYM_daily.csv files created by the intraday fetch.
"""
from __future__ import annotations
import os, sys, time
from datetime import datetime, timedelta, timezone

LOOKBACK_DAYS = 1100   # ~3 years -> >200 trading days before the 15m window start
OUT_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "ClaudeAlgo")
UNIVERSE = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","TSLA","JPM","BAC","GS","V","MA",
            "UNH","JNJ","LLY","PFE","XOM","CVX","WMT","COST","HD","NKE","MCD","KO","PG","CAT","BA","HON","SPY","QQQ"]

try:
    import pandas as pd
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from alpaca.data.enums import Adjustment, DataFeed
except ImportError as e:
    print(f"ERROR: missing package ({e}). Run: pip install alpaca-py pandas"); sys.exit(1)

KEY = os.environ.get("ALPACA_API_KEY"); SEC = os.environ.get("ALPACA_SECRET_KEY")
if not KEY or not SEC:
    print("ERROR: ALPACA_API_KEY / ALPACA_SECRET_KEY not in environment."); sys.exit(1)

client = StockHistoricalDataClient(KEY, SEC)
start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
end   = datetime.now(timezone.utc) - timedelta(minutes=20)

print(f"Fetching 3yr daily for {len(UNIVERSE)} symbols -> {OUT_DIR}\n")
ok = 0
for i, sym in enumerate(UNIVERSE, 1):
    try:
        req = StockBarsRequest(symbol_or_symbols=sym, timeframe=TimeFrame(1, TimeFrameUnit.Day),
                               start=start, end=end, adjustment=Adjustment.ALL, feed=DataFeed.IEX)
        df = client.get_stock_bars(req).df
        if df is None or len(df) == 0:
            print(f"[{i}/{len(UNIVERSE)}] {sym}: EMPTY"); continue
        df = df.reset_index()
        ts = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
        out = pd.DataFrame({"datetime": ts, "open": df.open.astype(float), "high": df.high.astype(float),
                            "low": df.low.astype(float), "close": df.close.astype(float),
                            "volume": df.volume.astype(float)}).sort_values("datetime").reset_index(drop=True)
        out.to_csv(os.path.join(OUT_DIR, f"{sym}_daily.csv"), index=False)
        print(f"[{i}/{len(UNIVERSE)}] {sym}: {len(out)} daily bars  {out.datetime.min().date()} -> {out.datetime.max().date()}")
        ok += 1
    except Exception as e:
        print(f"[{i}/{len(UNIVERSE)}] {sym}: FAILED ({type(e).__name__}: {str(e)[:100]})")
    time.sleep(0.3)
print(f"\nDone. {ok}/{len(UNIVERSE)} daily files updated. Tell Claude 'daily done'.")
