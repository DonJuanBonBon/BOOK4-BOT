#!/usr/bin/env python3
"""
fetch_datalake.py -- build a deep, broad daily data lake for edge research.
RUN ON YOUR WINDOWS MACHINE.  pip install yfinance pandas ; python fetch_datalake.py

WHY yfinance here (not Alpaca): yfinance returns DECADES of split/dividend-adjusted daily bars,
where Alpaca's free tier caps at ~1 year. For long backtests and the SPY benchmark we need depth.

WHERE it writes: a DEDICATED folder (datalake/) so it never overwrites curated long-history files.
SURVIVORSHIP NOTE: this universe is current large/mid-caps (survivors). Results on it are biased
upward. For rigorous cross-sectional tests, prefer point-in-time index membership if available.
"""
from __future__ import annotations
import os, sys, time

OUT_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "ClaudeAlgo", "datalake")
START   = "2005-01-01"   # ~20 years; plenty of warmup + multiple regimes (2008, 2020, 2022)

# Broad, sector-diversified universe (~70 names) + SPY/sector ETFs. Edit freely.
UNIVERSE = [
 # mega/large tech
 "AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","ORCL","ADBE","CRM","CSCO","INTC","AMD","QCOM","TXN",
 # financials
 "JPM","BAC","WFC","GS","MS","C","V","MA","AXP","SCHW",
 # healthcare
 "UNH","JNJ","LLY","PFE","MRK","ABBV","TMO","ABT","DHR",
 # consumer
 "WMT","COST","HD","LOW","NKE","MCD","SBUX","KO","PEP","PG","CL","TGT",
 # industrials/energy/materials
 "CAT","BA","HON","GE","UPS","XOM","CVX","COP","LIN","FCX",
 # comms/utilities/re
 "DIS","NFLX","CMCSA","T","VZ","NEE","DUK","AMT","PLD",
 # benchmarks / sector ETFs
 "SPY","QQQ","IWM","XLK","XLF","XLE","XLV","XLY","XLP","XLI",
]

try:
    import pandas as pd, yfinance as yf
except ImportError as e:
    print(f"ERROR: {e}. Run: pip install yfinance pandas"); sys.exit(1)

os.makedirs(OUT_DIR, exist_ok=True)
print(f"Fetching {len(UNIVERSE)} symbols, daily, {START} -> today, split/div-adjusted -> {OUT_DIR}\n")
ok=[]; report=[]
for i, sym in enumerate(UNIVERSE, 1):
    try:
        df = yf.download(sym, start=START, interval="1d", auto_adjust=True, progress=False)
        if df is None or len(df)==0:
            print(f"[{i}/{len(UNIVERSE)}] {sym}: EMPTY"); report.append((sym,0)); continue
        df = df.reset_index()
        # yfinance may return MultiIndex columns when one ticker -> flatten
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        out = pd.DataFrame({
            "datetime": pd.to_datetime(df["Date"]).dt.tz_localize(None),
            "open": df["Open"].astype(float), "high": df["High"].astype(float),
            "low": df["Low"].astype(float), "close": df["Close"].astype(float),
            "volume": df["Volume"].astype(float),
        }).dropna().sort_values("datetime")
        out.to_csv(os.path.join(OUT_DIR, f"{sym}_daily.csv"), index=False)
        ok.append(sym); report.append((sym,len(out)))
        print(f"[{i}/{len(UNIVERSE)}] {sym}: {len(out)} bars  {out.datetime.min().date()} -> {out.datetime.max().date()}")
    except Exception as e:
        print(f"[{i}/{len(UNIVERSE)}] {sym}: FAILED ({type(e).__name__}: {str(e)[:90]})"); report.append((sym,-1))
    time.sleep(0.4)

print("\n================ COVERAGE ================")
print(f"Succeeded: {len(ok)}/{len(UNIVERSE)}")
short=[s for s,n in report if 0<n<2000]
if short: print("Short history (<~8yr), check before cross-sectional use:", short)
fail=[s for s,n in report if n<=0]
if fail: print("Failed/empty:", fail)
print(f"\nData lake ready at {OUT_DIR}. Tell Claude 'datalake ready' and we'll point the harness at it.")
