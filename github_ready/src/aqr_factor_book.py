"""Multi-factor book from AQR free factor data (UPPER BOUND: long-short, levered, gross-of-cost).
Sleeves: All-asset Value, Momentum, Carry, Defensive (Century of Factor Premia) + Quality (QMJ USA).
ERC (inverse-vol) combine + vol-target. Compares to SPY on return AND drawdown, with $ outcomes."""
import numpy as np, pandas as pd, glob
D="/sessions/sharp-admiring-bardeen/mnt/Desktop/BOOK4-BOT/data_aqr"
SPYP="/sessions/sharp-admiring-bardeen/mnt/Desktop/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
cen=[x for x in glob.glob(f"{D}/*.xls*") if "Century" in x][0]
qmj=[x for x in glob.glob(f"{D}/*.xls*") if "Quality" in x][0]
c=pd.read_excel(cen, sheet_name="Century of Factor Premia", header=18, engine="openpyxl")
c["Date"]=pd.to_datetime(c["Date"]); c=c.set_index("Date")
cols={"Value":"All asset classes Value","Momentum":"All asset classes Momentum",
      "Carry":"All asset classes Carry","Defensive":"All asset classes Defensive"}
F=pd.DataFrame({k:c[v] for k,v in cols.items()})
q=pd.read_excel(qmj, sheet_name=0, header=18, engine="openpyxl"); q["DATE"]=pd.to_datetime(q["DATE"]); q=q.set_index("DATE")
F["Quality"]=q["USA"]
F.index=F.index.to_period("M"); F=F.dropna()
print(f"5-factor monthly data: {F.index.min()} -> {F.index.max()} ({len(F)} months)")
print("Factor correlation matrix:"); print(F.corr().round(2).to_string()); print()
# per-factor annualized Sharpe
for k in F: 
    r=F[k]; print(f"  {k:10s} Sharpe {(r.mean()*12)/(r.std()*np.sqrt(12)):.2f}  ann.ret {r.mean()*12*100:4.1f}%")
# ERC inverse-vol combine (trailing 36m, shifted -> no lookahead), vol-target 10%
iv=1.0/F.rolling(36).std(); w=iv.div(iv.sum(axis=1),axis=0).shift(1)
book=(w*F).sum(axis=1).dropna()
# SPY monthly
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M")
def met(r,ann=12):
    r=r.dropna(); eq=(1+r).cumprod(); y=len(r)/ann
    return dict(cagr=eq.iloc[-1]**(1/y)-1, dd=(eq/eq.cummax()-1).min(),
                sh=(r.mean()*ann)/(r.std()*np.sqrt(ann)) if r.std()>0 else np.nan,
                vol=r.std()*np.sqrt(ann), end=1000*float(eq.iloc[-1]))
bm=met(book); print(f"\nERC factor book (market-neutral alpha), full {book.index.min()}->{book.index.max()}:")
print(f"  Sharpe {bm['sh']:.2f}  ann.ret {bm['cagr']*100:.1f}%  vol {bm['vol']*100:.0f}%  maxDD {bm['dd']*100:.0f}%  corr-to-SPY {book.corr(spym.reindex(book.index)):+.2f}")
# overlap window with SPY (1993+) for head-to-head
ov=book.index.intersection(spym.dropna().index); b=book.loc[ov]; s=spym.loc[ov]
sm=met(s); 
# lever the (uncorrelated) book to SPY's vol over the overlap, and a SPY+overlay combo
lev=sm['vol']/b.std()/np.sqrt(12); blev=b*lev; blm=met(blev)
combo=(s + 0.5*b)  # 100% SPY + 50% factor-alpha overlay (alpha is ~self-funding/market-neutral)
cm=met(combo)
print(f"\nHEAD-TO-HEAD over {ov.min()}->{ov.max()} ({len(ov)} mo), $1,000 start:")
print(f"  SPY buy&hold          Sharpe {sm['sh']:.2f}  ret {sm['cagr']*100:4.1f}%  maxDD {sm['dd']*100:5.0f}%   $1,000 -> ${sm['end']:,.0f}")
print(f"  Factor book @SPY-vol  Sharpe {blm['sh']:.2f}  ret {blm['cagr']*100:4.1f}%  maxDD {blm['dd']*100:5.0f}%   $1,000 -> ${blm['end']:,.0f}")
print(f"  SPY + 50% alpha overlay Sharpe {cm['sh']:.2f}  ret {cm['cagr']*100:4.1f}% maxDD {cm['dd']*100:5.0f}%   $1,000 -> ${cm['end']:,.0f}")
