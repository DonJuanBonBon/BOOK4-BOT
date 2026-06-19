#!/usr/bin/env python3
r"""
aqr_probe.py - inspect the AQR Excel factor files so Claude can see their EXACT layout (no guessing),
then we build the precise loader. Costs nothing. Run on your Windows machine.

STEP 1 (manual download, free, no login): from https://www.aqr.com/Insights/Datasets download the
MONTHLY Excel for:
   - "How Do Factor Premia Vary Over Time? A Century of Evidence" (Century of Factor Premia, Monthly)
   - "Quality Minus Junk: Factors, Monthly"
   (optional also: "Value and Momentum Everywhere: Factors, Monthly")
Save the .xlsx files into:  this folder ->  BOOK4-BOT\data_aqr\

STEP 2: pip install pandas openpyxl
STEP 3: python aqr_probe.py
It writes data_aqr\_structure.txt describing every sheet + first rows, so we can wire it in correctly.
"""
import os, glob, sys
HERE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(HERE,"data_aqr")
try:
    import pandas as pd
except ImportError:
    print("Run: pip install pandas openpyxl"); sys.exit(1)
os.makedirs(DATA, exist_ok=True)
files=glob.glob(os.path.join(DATA,"*.xls*"))
if not files:
    print(f"No .xlsx files found in {DATA}. Download the AQR monthly Excel files there first (see top of this script)."); sys.exit(0)
out=os.path.join(DATA,"_structure.txt"); lines=[]
for f in files:
    lines.append("="*80); lines.append(f"FILE: {os.path.basename(f)}")
    try:
        xls=pd.ExcelFile(f, engine="openpyxl")
    except Exception as e:
        lines.append(f"  could not open: {e}"); continue
    lines.append(f"  sheets: {xls.sheet_names}")
    for sh in xls.sheet_names:
        try:
            df=pd.read_excel(f, sheet_name=sh, header=None, nrows=25, engine="openpyxl")
        except Exception as e:
            lines.append(f"  [{sh}] read error {e}"); continue
        lines.append("-"*60); lines.append(f"  SHEET '{sh}'  shape(first 25 rows x {df.shape[1]} cols):")
        for i,row in df.iterrows():
            vals=[str(v)[:18] for v in row.tolist()[:10]]
            lines.append(f"   r{i:02d}: "+" | ".join(vals))
text="\n".join(lines)
open(out,"w",encoding="utf-8").write(text)
print(f"Wrote structure -> {out}\n"); print(text[:3000])
print("\n...Tell Claude 'aqr structure ready' (the _structure.txt is in BOOK4-BOT\\data_aqr).")
