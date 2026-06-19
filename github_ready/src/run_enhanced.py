import numpy as np, pandas as pd
C="/sessions/sharp-admiring-bardeen/mnt/outputs/momentum_cache"
SPYP="/sessions/sharp-admiring-bardeen/mnt/Desktop/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl")
TOP_LIQUID=500; TOP_FRAC=0.25; COST=5/1e4; TD=12; FLOOR=5.0; ART=1.0; WIN=0.5
months=Mc.index
Rraw=Mc.pct_change(fill_method=None); Rc=Rraw.mask(Rraw.abs()>ART).clip(-WIN,WIN)
# market (SPY) monthly
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M")
m=spym.reindex(months)
# plain 12-1 momentum from cleaned returns
lr=np.log1p(Rc); mom=np.expm1(lr.rolling(TD).sum().shift(1))
# residual momentum: trailing-36m beta vs SPY, residual returns, cumulative
W=36
cov=(Rc.mul(m,axis=0)).rolling(W).mean() - Rc.rolling(W).mean().mul(m.rolling(W).mean(),axis=0)
var=m.rolling(W).var(ddof=0)
beta=cov.div(var,axis=0)
resid=Rc - beta.mul(m,axis=0)
resid_mom=resid.rolling(TD).sum().shift(1)

def port(signal):
    prev=set(); out=[]; idx=[]
    for i in range(W+TD+1,len(months)-1):
        live=(Mc.iloc[i]>=FLOOR)&Mc.iloc[i-TD].notna()&signal.iloc[i].notna()
        dv=Mdv.iloc[i].where(live); liquid=dv.dropna().nlargest(TOP_LIQUID).index
        ss=signal.iloc[i][liquid].dropna()
        if len(ss)<10: idx.append(months[i+1]); out.append(0.0); continue
        n=max(1,int(round(len(ss)*TOP_FRAC))); win=set(ss.nlargest(n).index)
        rn=Rc.iloc[i+1][list(win)].dropna(); g=rn.mean() if len(rn) else 0.0
        c=COST*(len(win.symmetric_difference(prev))/max(len(win),1))
        out.append(g-c); idx.append(months[i+1]); prev=win
    return pd.Series(out,index=pd.PeriodIndex(idx,freq="M"))

def volscale(p, target=0.12, w=6, cap=3.0):
    vol=p.rolling(w).std().shift(1)*np.sqrt(12)
    sc=(target/vol).clip(upper=cap).replace([np.inf,-np.inf],np.nan).fillna(0.0)
    return p*sc, sc

def met(r):
    r=r.dropna(); eq=(1+r).cumprod(); yrs=len(r)/12
    cagr=eq.iloc[-1]**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    sh=(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan
    return dict(cagr=cagr,dd=dd,sh=sh,worst=r.min(),skew=float(((r-r.mean())**3).mean()/r.std()**3), kurt=float(((r-r.mean())**4).mean()/r.std()**4-3))
def show(name,r):
    f=met(r); cut=r.index[int(len(r)*0.6)]; o=met(r.loc[cut:])
    print(f"{name:30s} FULL cagr {f['cagr']*100:5.1f}% dd {f['dd']*100:6.1f}% Sh {f['sh']:.2f} worstMo {f['worst']*100:5.1f}% skew {f['skew']:+.2f} kurt {f['kurt']:4.1f} | OOS cagr {o['cagr']*100:5.1f}% dd {o['dd']*100:6.1f}% Sh {o['sh']:.2f}")

plain=port(mom); residm=port(resid_mom)
plain_vs,sc1=volscale(plain); resid_vs,sc2=volscale(residm)
spy_r=m.reindex(plain.index).fillna(0)
print("CRASH-RESISTANCE TEST (survivorship-free, cleaned, monthly; OOS=last 40%)")
print("-"*150)
show("PLAIN momentum", plain)
show("RESIDUAL momentum", residm)
show("PLAIN + vol-scaled (12%)", plain_vs)
show("RESIDUAL + vol-scaled (combined)", resid_vs)
show("SPY buy&hold", spy_r)
print(f"\navg leverage applied: plain-vs {sc1.mean():.2f}x  resid-vs {sc2.mean():.2f}x  (cap 3x)")
