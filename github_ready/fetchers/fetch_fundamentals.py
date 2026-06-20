#!/usr/bin/env python3
r"""
fetch_fundamentals.py - pull EODHD quarterly fundamentals (point-in-time via filing_date) for the
3,287 ever-liquid tickers, keeping ONLY the fields needed for VALUE + QUALITY. Resumable.
PREREQ: EODHD plan includes Fundamentals; key in env. Run on your Windows machine.
   $env:EODHD_API_KEY = "your_key"
   pip install requests pandas
   python "BOOK4-BOT\fetch_fundamentals.py"        # ~3,300 calls, ~15-30 min, resumable (rerun to continue)
Output -> BOOK4-BOT\data_fundamentals\fund_shard_*.csv.gz (tidy: ticker,period,filing_date,<fields>)
"""
from __future__ import annotations
import os, sys, time, json, glob
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"data_fundamentals")
BASE="https://eodhd.com/api/fundamentals"; BATCH=500
BS_FIELDS=["totalStockholderEquity","totalAssets","longTermDebt","shortLongTermDebtTotal","netDebt",
           "commonStockSharesOutstanding","totalCurrentAssets","totalCurrentLiabilities","inventory"]
IS_FIELDS=["totalRevenue","grossProfit","netIncome","operatingIncome","ebit","costOfRevenue"]
try:
    import requests, pandas as pd
except ImportError as e:
    print(f"Run: pip install requests pandas ({e})"); sys.exit(1)
KEY=os.environ.get("EODHD_API_KEY")
if not KEY: print('EODHD_API_KEY not set. Run: $env:EODHD_API_KEY = "your_key"'); sys.exit(1)
tickers=[t.strip() for t in open(os.path.join(OUT,"liquid_tickers.txt")) if t.strip()]
prog=os.path.join(OUT,"_fund_progress.json")
done=set(json.load(open(prog)).get("done",[])) if os.path.exists(prog) else set()
todo=[t for t in tickers if t not in done]
print(f"fundamentals: {len(tickers)} tickers, {len(done)} done, {len(todo)} to fetch")
shard=len(glob.glob(os.path.join(OUT,"fund_shard_*.csv.gz"))); buf=[]; processed=list(done); t0=time.time()
def get(t):
    for a in range(4):
        try:
            r=requests.get(f"{BASE}/{t}.US", params={"api_token":KEY,"fmt":"json"}, timeout=30)
            if r.status_code==200: return r.json()
            if r.status_code in (404,400): return None
            if r.status_code==429: time.sleep(5*(a+1)); continue
            return None
        except Exception: time.sleep(2*(a+1))
    return None
for i,t in enumerate(todo,1):
    d=get(t)
    if d and isinstance(d,dict):
        fin=d.get("Financials",{}) or {}
        bs=(fin.get("Balance_Sheet",{}) or {}).get("quarterly",{}) or {}
        isq=(fin.get("Income_Statement",{}) or {}).get("quarterly",{}) or {}
        for period,brow in bs.items():
            irow=isq.get(period,{}) or {}
            row={"ticker":t,"period":period,"filing_date":brow.get("filing_date") or irow.get("filing_date")}
            for f in BS_FIELDS: row[f]=brow.get(f)
            for f in IS_FIELDS: row[f]=irow.get(f)
            buf.append(row)
    processed.append(t)
    if i%200==0: print(f"  {i}/{len(todo)} ({i/max(time.time()-t0,1):.1f}/s) rows={len(buf)}")
    if i%BATCH==0 and buf:
        pd.DataFrame(buf).to_csv(os.path.join(OUT,f"fund_shard_{shard:03d}.csv.gz"),index=False,compression="gzip")
        shard+=1; buf=[]; json.dump({"done":processed},open(prog,"w"))
    time.sleep(0.15)
if buf: pd.DataFrame(buf).to_csv(os.path.join(OUT,f"fund_shard_{shard:03d}.csv.gz"),index=False,compression="gzip")
json.dump({"done":processed},open(prog,"w"))
print(f"\nDONE. Shards in {OUT}. Tell Claude 'fundamentals fetched'.")
