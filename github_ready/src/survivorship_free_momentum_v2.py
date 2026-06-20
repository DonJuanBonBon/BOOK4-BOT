import glob, numpy as np, pandas as pd
UNI="data/datalake_eodhd/universe"
SPYP="data/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
TOP_LIQUID=500; TOP_FRAC=0.25; COST_BPS=5.0; TD=12; PRICE_FLOOR=5.0
ARTIFACT=1.0   # |monthly ret|>100% = data error -> drop
WINSOR=0.5     # clip remaining monthly returns to +/-50%

parts=[]
for f in sorted(glob.glob(f"{UNI}/shard_*.csv.gz")):
    d=pd.read_csv(f); d["dt"]=pd.to_datetime(d["date"]); d["ym"]=d["dt"].dt.to_period("M"); d["dv"]=d["close"]*d["volume"]
    parts.append(d.groupby(["ticker","ym"]).agg(close=("close","last"),dv=("dv","mean")).reset_index())
m=pd.concat(parts,ignore_index=True).groupby(["ticker","ym"]).agg(close=("close","last"),dv=("dv","mean")).reset_index()
Mc=m.pivot(index="ym",columns="ticker",values="close").sort_index()
Mdv=m.pivot(index="ym",columns="ticker",values="dv").sort_index()
months=Mc.index

Rraw=Mc.pct_change(fill_method=None)
n_art=int((Rraw.abs()>ARTIFACT).sum().sum())
Rc=Rraw.mask(Rraw.abs()>ARTIFACT)               # drop data-error months
Rc=Rc.clip(-WINSOR, WINSOR)                       # winsorize survivors
print(f"matrix {Mc.shape[0]}m x {Mc.shape[1]} tickers | artifact name-months dropped (|ret|>100%): {n_art:,}")
lr=np.log1p(Rc); mom=np.expm1(lr.rolling(TD).sum().shift(1))   # clean 12-1 momentum from returns

spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M")

def run(survivors=False):
    cols=Mc.columns[Mc.iloc[-1].notna().values] if survivors else Mc.columns
    Mc_u,Mdv_u,mom_u,R_u=Mc[cols],Mdv[cols],mom[cols],Rc[cols]
    prev=set(); port=[]; idx=[]
    for i in range(TD+1,len(months)-1):
        live=(Mc_u.iloc[i]>=PRICE_FLOOR)&Mc_u.iloc[i-TD].notna()&mom_u.iloc[i].notna()
        dv=Mdv_u.iloc[i].where(live)
        liquid=dv.dropna().nlargest(TOP_LIQUID).index
        mm=mom_u.iloc[i][liquid].dropna()
        if len(mm)<10: idx.append(months[i+1]); port.append(0.0); continue
        n=max(1,int(round(len(mm)*TOP_FRAC))); winners=set(mm.nlargest(n).index)
        rn=R_u.iloc[i+1][list(winners)].dropna(); gross=rn.mean() if len(rn) else 0.0
        cost=(COST_BPS/1e4)*(len(winners.symmetric_difference(prev))/max(len(winners),1))
        port.append(gross-cost); idx.append(months[i+1]); prev=winners
    return pd.Series(port,index=pd.PeriodIndex(idx,freq="M"))

def met(r):
    eq=(1+r).cumprod(); yrs=len(r)/12; cagr=eq.iloc[-1]**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    sh=(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan; return cagr,dd,sh
def rep(r,name):
    cut=r.index[int(len(r)*0.6)]; cf,df_,sf=met(r); co,do,so=met(r.loc[cut:])
    sp=spym.reindex(r.loc[cut:].index).fillna(0); scg,sdd,_=met(sp)
    print(f"{name:26s} FULL {cf*100:5.1f}%/{df_*100:6.1f}%  OOS {co*100:5.1f}%/{do*100:6.1f}% Sharpe {so:.2f} | SPY OOS {scg*100:4.1f}%/{sdd*100:5.1f}%")

print("\n=== CLEANED results (price>=$5, artifacts dropped, winsorized +/-50%) ===")
rep(run(False),"Survivorship-FREE")
rep(run(True ),"Survivors-ONLY (biased)")
print("(monthly engine, top-500 liquid, top-quartile 12-1 momentum, 5bps; OOS=last 40%)")
