import numpy as np, pandas as pd, glob, os
import panel_strategies as P
from edge_harness import _panel_portfolio
C="/sessions/sharp-admiring-bardeen/mnt/outputs/momentum_cache"
SPYP="/sessions/sharp-admiring-bardeen/mnt/Desktop/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
FUT="/sessions/sharp-admiring-bardeen/mnt/Desktop--ClaudeAlgo/datalake_futures"
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl"); VQ=pd.read_pickle(f"{C}/sleeves_vq.pkl")
ART=1.0;WIN=0.5;FLOOR=5.0;TOP=500;Q=0.20;TX=5/1e4;BW=36;TD=12;START=BW+TD+1
months=Mc.index
Rc=Mc.pct_change(fill_method=None).mask(Mc.pct_change(fill_method=None).abs()>ART).clip(-WIN,WIN)
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M"); mkt=spym.reindex(months)
cov=(Rc.mul(mkt,axis=0)).rolling(BW).mean()-Rc.rolling(BW).mean().mul(mkt.rolling(BW).mean(),axis=0)
beta=cov.div(mkt.rolling(BW).var(ddof=0),axis=0); resid=Rc-beta.mul(mkt,axis=0)
resid_mom=resid.rolling(TD).sum().shift(1); trail_vol=Rc.rolling(TD).std()
def xs(signal,ls=False,borrow=0.03):
    prev=pd.Series(dtype=float);out=[];idx=[]
    for i in range(START,len(months)-1):
        live=(Mc.iloc[i]>=FLOOR)&Mc.iloc[i-TD].notna()&signal.iloc[i].notna()&beta.iloc[i].notna()
        liquid=Mdv.iloc[i].where(live).dropna().nlargest(TOP).index; ss=signal.iloc[i][liquid].dropna()
        if len(ss)<20: out.append(0.0);idx.append(months[i+1]);prev=pd.Series(dtype=float);continue
        k=max(1,int(round(len(ss)*Q)));L=ss.nlargest(k).index;w=pd.Series(0.0,index=Mc.columns);w[L]=1/k
        if ls:
            Sh=ss.nsmallest(k).index;w[Sh]=-1/k;ret=Rc.iloc[i+1][L].mean()-Rc.iloc[i+1][Sh].mean();sn=1.0
        else: ret=Rc.iloc[i+1][L].mean();sn=0.0
        wa,pa=w.align(prev,fill_value=0.0);out.append((ret if ret==ret else 0)-TX*(wa-pa).abs().sum()-(borrow/12)*sn);idx.append(months[i+1]);prev=w
    return pd.Series(out,index=pd.PeriodIndex(idx,freq="M"))
s1=xs(resid_mom,borrow=0); s3=xs(-trail_vol,borrow=0); s4=VQ["MOM_ls"]; sV=VQ["VALUE"]
def lcf(s): return pd.read_csv(f"{FUT}/{s}_daily.csv",parse_dates=["datetime"]).set_index("datetime").sort_index()["close"]
futs=sorted(os.path.basename(f).replace("_daily.csv","") for f in glob.glob(f"{FUT}/*_daily.csv"))
fc=pd.DataFrame({s:lcf(s) for s in futs}).sort_index();fcr=fc.pct_change(fill_method=None).fillna(0.0)
ftd,_,_=_panel_portfolio(P.futures_trend(fc),fcr,3.0);s2=((1+ftd).resample("ME").prod()-1);s2.index=s2.index.to_period("M")
S=pd.DataFrame({"resMom_L":s1,"futTrend":s2,"lowVol_L":s3,"LS_resMom":s4,"VALUE_ls":sV}).dropna()
print(f"window {S.index.min()} -> {S.index.max()} ({len(S)} mo) | 5-sleeve book (VALUE added, quality dropped)")
print("correlation matrix:"); print(S.corr().round(2).to_string()); print()
iv=1.0/S.rolling(12).std();w=iv.div(iv.sum(axis=1),axis=0).shift(1);book=(w*S).sum(axis=1).dropna()
bv=book.rolling(6).std().shift(1)*np.sqrt(12);sc=(0.10/bv).clip(upper=2.0).replace([np.inf,-np.inf],np.nan).fillna(0.0);bvt=(book*sc).dropna()
def met(r):
    r=r.dropna();eq=(1+r).cumprod();y=len(r)/12
    return eq.iloc[-1]**(1/y)-1,(eq/eq.cummax()-1).min(),(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan,float(r.corr(mkt.reindex(r.index))),1000*float(eq.iloc[-1])
def show(n,r):
    f=met(r);rr=r.dropna();cut=rr.index[int(len(rr)*0.6)];o=met(r.loc[cut:]);oend=1000*float((1+r.loc[cut:].dropna()).cumprod().iloc[-1])
    print(f"{n:24s} FULL Sh{f[2]:5.2f} dd{f[1]*100:6.1f}% corrSPY{f[3]:+.2f} $1k->${f[4]:>8,.0f} | OOS Sh{o[2]:5.2f} ret{o[0]*100:5.1f}% dd{o[1]*100:6.1f}% $1k->${oend:>7,.0f}")
print("PER-SLEEVE:"); [show(c,S[c].loc[book.index]) for c in S.columns]
print("\nBOOK:"); show("  ERC book",book); show("  ERC book + vol-target",bvt); show("SPY buy&hold",mkt.reindex(book.index).fillna(0))

print("\n=== EQUAL-RISK TEST: lever the ERC book to SPY's volatility, head-to-head ($1,000) ===")
def headtohead(label, r_book, r_spy):
    r_book=r_book.dropna(); r_spy=r_spy.reindex(r_book.index).fillna(0)
    lev=(r_spy.std()/r_book.std())
    bl=r_book*lev
    def m(r):
        eq=(1+r).cumprod(); y=len(r)/12
        return eq.iloc[-1]**(1/y)-1,(eq/eq.cummax()-1).min(),(r.mean()*12)/(r.std()*np.sqrt(12)),1000*float(eq.iloc[-1])
    bc,bd,bs,be=m(bl); sc,sd,ss,se=m(r_spy)
    print(f"  [{label}] book @ {lev:.1f}x (=SPY vol):  ret {bc*100:4.1f}%  maxDD {bd*100:5.0f}%  Sh {bs:.2f}  $1,000->${be:,.0f}")
    print(f"  [{label}] SPY buy&hold:                ret {sc*100:4.1f}%  maxDD {sd*100:5.0f}%  Sh {ss:.2f}  $1,000->${se:,.0f}")
    print(f"  [{label}] -> beats SPY on return? {bc>sc}   on drawdown? {abs(bd)<abs(sd)}")
full=book; cut=book.index[int(len(book)*0.6)]
headtohead("FULL", full, mkt)
headtohead("OOS ", book.loc[cut:], mkt)
