#!/usr/bin/env python3
"""
fetch_eodhd.py - survivorship-FREE equity data via EODHD (includes DELISTED companies).
RUN ON YOUR WINDOWS MACHINE after subscribing to EODHD (~$20/mo) and setting your key:
    setx EODHD_API_KEY "your_key_here"   (then reopen the terminal)
    pip install requests pandas
    python fetch_eodhd.py

STAGED ON PURPOSE (no wasted quota / no mistakes):
  STAGE 1 (this script): (a) download the full ACTIVE and DELISTED US symbol lists and save them,
                         (b) pull EOD history for a tiny TEST set INCLUDING a delisted name, to PROVE
                            your plan returns delisted data. Cheap - a handful of calls.
  STAGE 2 (we do together next): use the saved symbol lists (+ verify EODHD historical index
                         constituents on your account) to build a proper point-in-time, delisted-
                         inclusive universe, then re-run momentum survivorship-free.

Endpoints verified from EODHD docs:
  symbol list : https://eodhd.com/api/exchange-symbol-list/US?api_token=KEY&fmt=json[&delisted=1]
  EOD history : https://eodhd.com/api/eod/{TICKER}?api_token=KEY&fmt=json&from=YYYY-MM-DD
                (delisted tickers use an '_old' suffix, e.g. LEH_old.US; EOD works the same way)
"""
from __future__ import annotations
import os, sys, time, json
OUT = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "ClaudeAlgo", "datalake_eodhd")
SYM_DIR = os.path.join(OUT, "_symbols")
START = "2000-01-01"
BASE = "https://eodhd.com/api"
# Stage-1 connectivity test set: a few survivors + KNOWN delisted large-caps (failures) to prove inclusion.
TEST_TICKERS = ["AAPL.US", "MSFT.US", "LEH_old.US", "BSC_old.US", "ENE_old.US"]  # Lehman, Bear Stearns, Enron

try:
    import pandas as pd, requests
except ImportError as e:
    print(f"ERROR: {e}. Run: pip install requests pandas"); sys.exit(1)
KEY = os.environ.get("EODHD_API_KEY")
if not KEY:
    print("ERROR: EODHD_API_KEY not set. Run: setx EODHD_API_KEY \"your_key\" then reopen the terminal."); sys.exit(1)

os.makedirs(SYM_DIR, exist_ok=True)

def get(url, params):
    for a in range(4):
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 200: return r
            print(f"   HTTP {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"   retry ({type(e).__name__})")
        time.sleep(2*(a+1))
    return None

print("STAGE 1a: downloading US symbol lists (active + delisted) ...")
for tag, extra in [("active", {}), ("delisted", {"delisted":"1"})]:
    r = get(f"{BASE}/exchange-symbol-list/US", {"api_token":KEY,"fmt":"csv", **extra})
    if r is None: print(f"   {tag}: FAILED"); continue
    p = os.path.join(SYM_DIR, f"US_{tag}_symbols.csv")
    open(p,"w",encoding="utf-8").write(r.text)
    n = max(0, r.text.count("\n")-1)
    print(f"   {tag}: {n} symbols saved -> {p}")

print("\nSTAGE 1b: EOD test pull (incl. delisted) to confirm survivorship-free access ...")
def adj_ohlcv(rows):
    df = pd.DataFrame(rows)
    if df.empty or "adjusted_close" not in df: return None
    f = df["adjusted_close"]/df["close"]
    out = pd.DataFrame({"datetime":pd.to_datetime(df["date"]),
        "open":df["open"]*f,"high":df["high"]*f,"low":df["low"]*f,
        "close":df["adjusted_close"],"volume":df["volume"]}).dropna().sort_values("datetime")
    return out
for t in TEST_TICKERS:
    r = get(f"{BASE}/eod/{t}", {"api_token":KEY,"fmt":"json","from":START,"period":"d"})
    if r is None: print(f"   {t:12s} FAILED"); continue
    try:
        out = adj_ohlcv(json.loads(r.text))
    except Exception as e:
        print(f"   {t:12s} parse error {e}"); continue
    if out is None or len(out)==0:
        print(f"   {t:12s} no data (check ticker / plan)"); continue
    out.to_csv(os.path.join(OUT, f"{t.replace('.US','').replace('_old','_DELISTED')}_daily.csv"), index=False)
    tag = "DELISTED" if "_old" in t else "active"
    print(f"   {t:12s} [{tag}] {len(out)} bars  {out.datetime.min().date()} -> {out.datetime.max().date()}")
print(f"\nStage 1 done. Symbol lists in {SYM_DIR}. If the DELISTED test tickers returned data, your plan")
print("is survivorship-free and we can build the real universe. Tell Claude 'eodhd stage 1 done'.")
