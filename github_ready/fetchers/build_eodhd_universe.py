#!/usr/bin/env python3
r"""
build_eodhd_universe.py - fetch a SURVIVORSHIP-FREE liquid-universe dataset from EODHD ($20 EOD plan).
Fetches adjusted close + volume (2005 onward) for EVERY NYSE/NASDAQ COMMON STOCK that ever existed
(active + delisted), so failures are included. Output = compact gz SHARDS (not 21k files) + a
resumable progress file. We liquidity-screen later, at test time.

Run on your Windows machine:
    $env:EODHD_API_KEY = "your_key"      # if not already in this terminal
    pip install requests pandas
    python build_eodhd_universe.py        # ~20-40 min, resumable: just rerun if interrupted

Output folder: ClaudeAlgo/datalake_eodhd/universe/  (shard_*.csv.gz; columns date,ticker,close,volume)
"""
from __future__ import annotations
import os, sys, time, json, glob
SYM = os.path.join(os.path.expanduser("~"),"OneDrive","Desktop","ClaudeAlgo","datalake_eodhd","_symbols")
OUT = os.path.join(os.path.expanduser("~"),"OneDrive","Desktop","ClaudeAlgo","datalake_eodhd","universe")
START="2005-01-01"; BASE="https://eodhd.com/api"; BATCH=1000
BLOCK={"WT","WS","U","UN","RT","R","W","P","WI","WD","WSA","WSB","CL","PR"}
try:
    import pandas as pd, requests
except ImportError as e:
    print(f"ERROR {e}. Run: pip install requests pandas"); sys.exit(1)
KEY=os.environ.get("EODHD_API_KEY")
if not KEY: print('EODHD_API_KEY not set. Run: $env:EODHD_API_KEY = "your_key"'); sys.exit(1)
os.makedirs(OUT, exist_ok=True)

def clean(code):
    code=str(code)
    if "-" in code:
        tail=code.split("-")[-1].upper()
        if tail in BLOCK: return None
        if any(ch.isdigit() for ch in tail): return None
        if tail not in ("A","B","C"): return None
    if "." in code and not code.endswith((".A",".B")): return None
    return code

def universe():
    a=pd.read_csv(os.path.join(SYM,"US_active_symbols.csv"))
    d=pd.read_csv(os.path.join(SYM,"US_delisted_symbols.csv"))
    out=[]
    for df in (a,d):
        cs=df[(df["Type"]=="Common Stock") & (df["Exchange"].isin(["NYSE","NASDAQ"]))]
        for c in cs["Code"].astype(str):
            cc=clean(c)
            if cc: out.append(cc)
    return sorted(set(out))

def get(tkr):
    for a in range(4):
        try:
            r=requests.get(f"{BASE}/eod/{tkr}.US",
                           params={"api_token":KEY,"fmt":"json","from":START,"period":"d"},timeout=30)
            if r.status_code==200: return r.json()
            if r.status_code==404: return []
            if r.status_code==429: time.sleep(5*(a+1)); continue
            return []
        except Exception:
            time.sleep(2*(a+1))
    return []

prog=os.path.join(OUT,"_progress.json")
done=set()
if os.path.exists(prog):
    try: done=set(json.load(open(prog)).get("done",[]))
    except Exception: done=set()

uni=universe()
todo=[t for t in uni if t not in done]
print(f"Universe: {len(uni)} common stocks (NYSE/NASDAQ, active+delisted). Done: {len(done)}. To fetch: {len(todo)}")
shard_idx=len(glob.glob(os.path.join(OUT,"shard_*.csv.gz")))
buf=[]; processed=list(done); t0=time.time()
for i,tkr in enumerate(todo,1):
    js=get(tkr)
    if js:
        for row in js:
            ac=row.get("adjusted_close"); v=row.get("volume")
            if ac:
                buf.append((row["date"], tkr, ac, v))
    processed.append(tkr)
    if i % 200 == 0:
        el=time.time()-t0; print(f"  {i}/{len(todo)}  ({i/max(el,1):.0f}/s)  rows={len(buf)}")
    if i % BATCH == 0 and buf:
        pd.DataFrame(buf,columns=["date","ticker","close","volume"]).to_csv(
            os.path.join(OUT,f"shard_{shard_idx:04d}.csv.gz"),index=False,compression="gzip")
        shard_idx+=1; buf=[]; json.dump({"done":processed},open(prog,"w"))
if buf:
    pd.DataFrame(buf,columns=["date","ticker","close","volume"]).to_csv(
        os.path.join(OUT,f"shard_{shard_idx:04d}.csv.gz"),index=False,compression="gzip")
json.dump({"done":processed},open(prog,"w"))
print(f"\nDONE. Shards in {OUT}. Processed {len(processed)} tickers. Tell Claude 'universe fetched'.")
