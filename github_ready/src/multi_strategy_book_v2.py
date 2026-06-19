"""Corrected multi-strategy book: drop dead/mis-specified sleeves, combine only POSITIVE-edge sleeves.
Sleeves: 1) residual momentum long-only, 2) futures trend (monthly), 3) LOW-VOL long-only (fixed; was naive BAB),
4) L/S residual momentum. ERC (inverse-vol) + vol-target. No look-ahead."""
import numpy as np, pandas as pd, glob, os
C="/sessions/sharp-admiring-bardeen/mnt/outputs/momentum_cache"
SPYP="/sessions/sharp-admiring-bardeen/mnt/Desktop/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
FUT="/sessions/sharp-admiring-bardeen/mnt/Desktop--ClaudeAlgo/datalake_futures"
import panel_strategies as P
from edge_harness import _panel_portfolio
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl")
TOP=500; Q=0.20; TX=5/1e4; FLOOR=5.0; ART=1.0; WIN=0.5; BW=36; TD=12; START=BW+TD+1
months=Mc.index
Rc=Mc.pct_change(fill_method=None).mask(Mc.pct_change(fill_method=None).abs()>ART).clip(-WIN,WIN)
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M"); mkt=spym.reindex(months)
cov=(Rc.mul(mkt,axis=0)).rolling(BW).mean()-Rc.rolling(BW).mean().mul(mkt.rolling(BW).mean(),axis=0)
beta=cov.div(mkt.rolling(BW).var(ddof=0),axis=0); resid=Rc-beta.mul(mkt,axis=0)
resid_mom=resid.rolling(TD).sum().shift(1); trail_vol=Rc.rolling(TD).std()
def xs(signal, ls=False, borrow=0.03):
    prev=pd.Series(dtype=float); out=[]; idx=[]
    for i in range(START,len(months)-1):
        live=(Mc.iloc[i]>=FLOOR)&Mc.iloc[i-TD].notna()&signal.iloc[i].notna()&beta.iloc[i].notna()
        liquid=Mdv.iloc[i].where(live).dropna().nlargest(TOP).index
        ss=signal.iloc[i][liquid].dropna()
        if len(ss)<20: out.append(0.0); idx.append(months[i+1]); prev=pd.Series(dtype=float); continue
        k=max(1,int(round(len(ss)*Q))); longs=ss.nlargest(k).index
        w=pd.Series(0.0,index=Mc.columns); w[longs]=1.0/k
        if ls:
            shorts=ss.nsmallest(k).index; w[shorts]=-1.0/k
            ret=Rc.iloc[i+1][longs].mean()-Rc.iloc[i+1][shorts].mean(); sn=1.0
        else:
            ret=Rc.iloc[i+1][longs].mean(); sn=0.0
        wa,pa=w.align(prev,fill_value=0.0); turn=(wa-pa).abs().sum()
        out.append((ret if ret==ret else 0.0)-TX*turn-(borrow/12)*sn); idx.append(months[i+1]); prev=w
    return pd.Series(out,index=pd.PeriodIndex(idx,freq="M"))
s1=xs(resid_mom,ls=False,borrow=0)     # residual momentum long
s3=xs(-trail_vol,ls=False,borrow=0)    # LOW-VOL long-only (fixed)
s4=xs(resid_mom,ls=True)               # L/S residual momentum
def lcf(s): return pd.read_csv(f"{FUT}/{s}_daily.csv",parse_dates=["datetime"]).set_index("datetime").sort_index()["close"]
futs=sorted(os.path.basename(f).replace("_daily.csv","") for f in glob.glob(f"{FUT}/*_daily.csv"))
fc=pd.DataFrame({s:lcf(s) for s in futs}).sort_index(); fcr=fc.pct_change(fill_method=None).fillna(0.0)
ftd,_,_=_panel_portfolio(P.futures_trend(fc),fcr,3.0); s2=((1+ftd).resample("ME").prod()-1); s2.index=s2.index.to_period("M")
S=pd.DataFrame({"resMom_L":s1,"futTrend":s2,"lowVol_L":s3,"LS_resMom":s4}).dropna()
print("Correlation matrix:"); print(S.corr().round(2).to_string()); print()
iv=1.0/S.rolling(12).std(); w=iv.div(iv.sum(axis=1),axis=0).shift(1); book=(w*S).sum(axis=1).dropna()
bv=book.rolling(6).std().shift(1)*np.sqrt(12); sc=(0.10/bv).clip(upper=2.0).replace([np.inf,-np.inf],np.nan).fillna(0.0); book_vt=(book*sc).dropna()
def met(r):
    r=r.dropna(); eq=(1+r).cumprod(); y=len(r)/12
    return (eq.iloc[-1]**(1/y)-1,(eq/eq.cummax()-1).min(),(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan,float(r.corr(mkt.reindex(r.index))))
def show(n,r):
    f=met(r); rr=r.dropna(); cut=rr.index[int(len(rr)*0.6)]; o=met(r.loc[cut:])
    full_end=1000*float((1+rr).cumprod().iloc[-1]); oos=r.loc[cut:].dropna(); oos_end=1000*float((1+oos).cumprod().iloc[-1])
    print(f"{n:24s} FULL Sh{f[2]:5.2f} dd{f[1]*100:6.1f}%  $1,000->${full_end:>9,.0f}  | OOS Sh{o[2]:5.2f} dd{o[1]*100:6.1f}%  $1,000->${oos_end:>8,.0f}")
print("PER-SLEEVE:");  [show(c,S[c].loc[book.index]) for c in S.columns]
print("\nBOOK:"); show("  ERC book",book); show("  ERC book + vol-target",book_vt)
show("SPY buy&hold",mkt.reindex(book.index).fillna(0))
print(f"\navg leverage {sc.reindex(book_vt.index).mean():.2f}x | months {len(book)}")
