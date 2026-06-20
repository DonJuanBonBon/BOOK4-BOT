import numpy as np, pandas as pd, glob, os
import panel_strategies as P
from edge_harness import _panel_portfolio
C="data/momentum_cache"
FUT="data/datalake_futures"
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl"); VQ=pd.read_pickle(f"{C}/sleeves_vq.pkl")
ART=1.0;WIN=0.5;FLOOR=5.0;TOP=500;Q=0.20;TX=5/1e4;BW=36;TD=12;START=BW+TD+1
months=Mc.index
Rc=Mc.pct_change(fill_method=None).mask(Mc.pct_change(fill_method=None).abs()>ART).clip(-WIN,WIN)
SPYP="data/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
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
s1=xs(resid_mom,borrow=0); s3=xs(-trail_vol,borrow=0)
def lcf(s): return pd.read_csv(f"{FUT}/{s}_daily.csv",parse_dates=["datetime"]).set_index("datetime").sort_index()["close"]
futs=sorted(os.path.basename(f).replace("_daily.csv","") for f in glob.glob(f"{FUT}/*_daily.csv"))
fc=pd.DataFrame({s:lcf(s) for s in futs}).sort_index();fcr=fc.pct_change(fill_method=None).fillna(0.0)
ftd,_,_=_panel_portfolio(P.futures_trend(fc),fcr,3.0);s2=((1+ftd).resample("ME").prod()-1);s2.index=s2.index.to_period("M")
S=pd.DataFrame({"resMom_L":s1,"futTrend":s2,"lowVol_L":s3,"LS_resMom":VQ["MOM_ls"],"VALUE_ls":VQ["VALUE"]}).dropna()
iv=1.0/S.rolling(12).std();w=iv.div(iv.sum(axis=1),axis=0).shift(1);book=(w*S).sum(axis=1).dropna()
book.to_pickle(f"{C}/book5.pkl")
print(f"saved book5.pkl: {len(book)} months {book.index.min()}->{book.index.max()}  unlev ann.ret {book.mean()*12*100:.1f}% vol {book.std()*np.sqrt(12)*100:.1f}%")
