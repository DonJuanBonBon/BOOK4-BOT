#!/usr/bin/env python3
r"""
fetch_databento_intraday.py - free/cheap 1-minute ES/NQ futures bars via Databento ($125 free credits).
STAGED so you never blow the free credits by accident:
  RUN 1 (cost check): prints the USD cost of the request and DOES NOT download.
  RUN 2 (download):    set CONFIRM_DOWNLOAD=1 after you've seen the cost is acceptable.

Setup on your Windows machine (sign up at databento.com -> get API key + $125 credits):
    $env:DATABENTO_API_KEY = "your_key"
    pip install databento pandas
    python fetch_databento_intraday.py                 # cost check only
    $env:CONFIRM_DOWNLOAD = "1"; python fetch_databento_intraday.py   # actually download

Verified against Databento docs: dataset GLBX.MDP3, schema 'ohlcv-1m', continuous front-month
symbology stype_in='continuous' with symbols like 'ES.c.0','NQ.c.0'. Output -> datalake_futures_intraday/.
"""
from __future__ import annotations
import os, sys
OUT = os.path.join(os.path.expanduser("~"),"OneDrive","Desktop","ClaudeAlgo","datalake_futures_intraday")
DATASET="GLBX.MDP3"; SCHEMA="ohlcv-1m"; STYPE="continuous"
SYMBOLS=["ES.c.0","NQ.c.0"]            # continuous front-month
START="2019-01-01"; END=None           # None -> up to latest available
try:
    import pandas as pd, databento as db
except ImportError as e:
    print(f"ERROR {e}. Run: pip install databento pandas"); sys.exit(1)
KEY=os.environ.get("DATABENTO_API_KEY")
if not KEY: print('DATABENTO_API_KEY not set. Run: $env:DATABENTO_API_KEY = "your_key"'); sys.exit(1)
os.makedirs(OUT, exist_ok=True)
client=db.Historical(KEY)
end = END or pd.Timestamp.utcnow().strftime("%Y-%m-%d")

# ---- STAGE 1: cost check (no spend) ----
try:
    cost=client.metadata.get_cost(dataset=DATASET, symbols=SYMBOLS, stype_in=STYPE,
                                  schema=SCHEMA, start=START, end=end)
    print(f"Estimated cost for {SYMBOLS} {SCHEMA} {START}->{end}:  ${cost:.2f}  (you have $125 free credits)")
except Exception as e:
    print(f"cost check failed: {type(e).__name__}: {e}"); sys.exit(1)

if os.environ.get("CONFIRM_DOWNLOAD") != "1":
    print("\nCost check only. If acceptable, run again with:  $env:CONFIRM_DOWNLOAD = \"1\"")
    sys.exit(0)

# ---- STAGE 2: download ----
print("Downloading ...")
data=client.timeseries.get_range(dataset=DATASET, symbols=SYMBOLS, stype_in=STYPE,
                                 schema=SCHEMA, start=START, end=end)
df=data.to_df()                          # ts_event index (UTC), columns incl symbol, open,high,low,close,volume
df=df.reset_index()
tcol="ts_event" if "ts_event" in df.columns else df.columns[0]
df["datetime"]=pd.to_datetime(df[tcol], utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
symcol="symbol" if "symbol" in df.columns else None
for sym in SYMBOLS:
    base=sym.split(".")[0]
    sub=df[df[symcol]==sym] if symcol else df
    out=sub[["datetime","open","high","low","close","volume"]].dropna().sort_values("datetime")
    p=os.path.join(OUT,f"{base}_1m.csv")
    out.to_csv(p,index=False)
    print(f"  {base}: {len(out)} 1-min bars  {out.datetime.min()} -> {out.datetime.max()}  -> {p}")
print("\nDone. Tell Claude 'intraday futures ready'.")
