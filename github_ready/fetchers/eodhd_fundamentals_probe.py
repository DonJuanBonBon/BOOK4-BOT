#!/usr/bin/env python3
r"""
eodhd_fundamentals_probe.py - ONE-call probe of EODHD fundamentals so Claude sees the EXACT field layout
before we fetch the whole universe (no guessing the schema). Costs ~1 API call.
PREREQ: your EODHD plan must include FUNDAMENTALS (upgrade to "Fundamentals Data Feed" ~$59.99/mo).
Your existing key still works.
Run:  $env:EODHD_API_KEY = "your_key"   (if not set)
      pip install requests
      python "BOOK4-BOT\eodhd_fundamentals_probe.py"
Writes data_fundamentals\_structure.json (the keys/shape) so we build the value+quality fetcher correctly.
"""
import os, sys, json, glob
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"data_fundamentals")
try:
    import requests
except ImportError:
    print("Run: pip install requests"); sys.exit(1)
KEY=os.environ.get("EODHD_API_KEY")
if not KEY: print('EODHD_API_KEY not set. Run: $env:EODHD_API_KEY = "your_key"'); sys.exit(1)
os.makedirs(OUT, exist_ok=True)
r=requests.get("https://eodhd.com/api/fundamentals/AAPL.US", params={"api_token":KEY,"fmt":"json"}, timeout=30)
print("HTTP", r.status_code)
if r.status_code!=200:
    print("=> fundamentals NOT available on your plan yet:", r.text[:200])
    print("Upgrade to a fundamentals-inclusive EODHD plan, then re-run."); sys.exit(0)
d=r.json()
# dump the STRUCTURE (top-level keys + financial statement keys + one sample quarter), not the whole payload
struct={"top_level_keys": list(d.keys())}
fin=d.get("Financials",{})
struct["Financials_keys"]=list(fin.keys())
for stmt in ("Balance_Sheet","Income_Statement","Cash_Flow"):
    s=fin.get(stmt,{})
    q=s.get("quarterly",{})
    struct[f"{stmt}_quarterly_dates_sample"]=list(q.keys())[:3]
    if q:
        first=list(q.values())[0]
        struct[f"{stmt}_quarterly_fields"]=list(first.keys())
struct["Highlights_keys"]=list(d.get("Highlights",{}).keys())
struct["Valuation_keys"]=list(d.get("Valuation",{}).keys())
struct["SharesStats_keys"]=list(d.get("SharesStats",{}).keys())
json.dump(struct, open(os.path.join(OUT,"_structure.json"),"w"), indent=2)
print("Wrote data_fundamentals/_structure.json")
print(json.dumps(struct, indent=2)[:2500])
print("\nTell Claude 'fundamentals probe ready'.")
