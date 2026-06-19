#!/usr/bin/env python3
"""
fetch_futures.py - build a managed-futures price data lake (FREE, via yfinance continuous futures).
RUN ON YOUR WINDOWS MACHINE:  pip install yfinance pandas ; python fetch_futures.py
Writes SYM_daily.csv into ClaudeAlgo\datalake_futures\ (a SEPARATE folder - never overwrites equity data).
Purpose: a real, diversified managed-futures basket (commodities/rates/FX/index) to build a STRONGER
cross-asset trend sleeve than the 7 ETFs we used (which returned only ~4.5%/yr).
NOTE: yfinance continuous-future history varies by contract (~2000-2007 start); the coverage report
shows exactly what you got. yfinance gives back-adjusted continuous series (fine for a trend signal).
"""
from __future__ import annotations
import os, sys, time
OUT = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "ClaudeAlgo", "datalake_futures")
START = "2000-01-01"
# Diversified managed-futures basket (yfinance continuous-future symbols, '=F').
BASKET = {
 "GC=F":"gold","SI=F":"silver","HG=F":"copper","CL=F":"crude","NG=F":"natgas",
 "ZC=F":"corn","ZW=F":"wheat","ZS=F":"soybeans","KC=F":"coffee","SB=F":"sugar","CT=F":"cotton",
 "ZB=F":"ustreasury30y","ZN=F":"ustreasury10y","ZF=F":"ustreasury5y",
 "6E=F":"euro","6J=F":"yen","6B=F":"pound","6A=F":"aud",
 "ES=F":"sp500","NQ=F":"nasdaq","YM=F":"dow",
}
try:
    import pandas as pd, yfinance as yf
except ImportError as e:
    print(f"ERROR: {e}. Run: pip install yfinance pandas"); sys.exit(1)

os.makedirs(OUT, exist_ok=True)
print(f"Fetching {len(BASKET)} continuous futures, daily, {START}->today -> {OUT}\n")
ok=[]; rep=[]
for i,(sym,name) in enumerate(BASKET.items(),1):
    fn = sym.replace("=","_")   # GC=F -> GC_F (filesystem-safe)
    try:
        df = yf.download(sym, start=START, interval="1d", auto_adjust=True, progress=False)
        if df is None or len(df)==0:
            print(f"[{i}/{len(BASKET)}] {sym:5s} {name:13s} EMPTY"); rep.append((sym,0)); continue
        df = df.reset_index()
        df.columns = [c[0] if isinstance(c,tuple) else c for c in df.columns]
        out = pd.DataFrame({"datetime":pd.to_datetime(df["Date"]).dt.tz_localize(None),
                            "open":df["Open"].astype(float),"high":df["High"].astype(float),
                            "low":df["Low"].astype(float),"close":df["Close"].astype(float),
                            "volume":df["Volume"].astype(float)}).dropna().sort_values("datetime")
        out.to_csv(os.path.join(OUT,f"{fn}_daily.csv"),index=False)
        ok.append(sym); rep.append((sym,len(out)))
        print(f"[{i}/{len(BASKET)}] {sym:5s} {name:13s} {len(out)} bars  {out.datetime.min().date()} -> {out.datetime.max().date()}")
    except Exception as e:
        print(f"[{i}/{len(BASKET)}] {sym:5s} {name:13s} FAILED ({type(e).__name__}: {str(e)[:70]})"); rep.append((sym,-1))
    time.sleep(0.4)
print(f"\nDone. {len(ok)}/{len(BASKET)} futures saved to {OUT}. Tell Claude 'futures ready'.")
