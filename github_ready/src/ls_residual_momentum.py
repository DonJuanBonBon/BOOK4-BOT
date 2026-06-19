"""
Long-short MARKET-NEUTRAL residual momentum (Blitz/Huij/Martens signal, dollar-neutral construction).
Survivorship-free top-500-liquid universe (cached, cleaned). Monthly. NO look-ahead (signal at t uses
only past; trailing-36m beta; realize t+1). Models BOTH legs' transaction cost + short BORROW fee
(swept 1/3/5%/yr because momentum losers are often hard-to-borrow). Tests Barroso vol-scaling (which
SHOULD work on long-short). Optimized: residual computed with vectorized rolling matrix ops; cache reused.
"""
import numpy as np, pandas as pd
C="/sessions/sharp-admiring-bardeen/mnt/outputs/momentum_cache"
SPYP="/sessions/sharp-admiring-bardeen/mnt/Desktop/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl")
TOP_LIQUID=500; QUINT=0.20; TXBPS=5/1e4; TD=12; FLOOR=5.0; ART=1.0; WIN=0.5; BETA_W=36
months=Mc.index
Rraw=Mc.pct_change(fill_method=None); Rc=Rraw.mask(Rraw.abs()>ART).clip(-WIN,WIN)
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M"); mkt=spym.reindex(months)
# residual returns vs SPY (trailing 36m beta, past-only) -> residual 12-1 momentum
cov=(Rc.mul(mkt,axis=0)).rolling(BETA_W).mean() - Rc.rolling(BETA_W).mean().mul(mkt.rolling(BETA_W).mean(),axis=0)
var=mkt.rolling(BETA_W).var(ddof=0)
beta=cov.div(var,axis=0); resid=Rc - beta.mul(mkt,axis=0)
sig=resid.rolling(TD).sum().shift(1)         # residual 12-1 momentum, decided at t (past only)

def ls_returns():
    """Returns (spread_gross, turnover, short_notional) monthly series. Dollar-neutral equal-weight legs."""
    prev=pd.Series(dtype=float); rows=[]; idx=[]
    cols=Mc.columns
    for i in range(BETA_W+TD+1, len(months)-1):
        live=(Mc.iloc[i]>=FLOOR)&Mc.iloc[i-TD].notna()&sig.iloc[i].notna()
        dv=Mdv.iloc[i].where(live); liquid=dv.dropna().nlargest(TOP_LIQUID).index
        ss=sig.iloc[i][liquid].dropna()
        if len(ss)<20: idx.append(months[i+1]); rows.append((0.0,0.0,0.0)); prev=pd.Series(dtype=float); continue
        k=max(1,int(round(len(ss)*QUINT)))
        longs=ss.nlargest(k).index; shorts=ss.nsmallest(k).index
        w=pd.Series(0.0,index=cols); w[longs]=1.0/len(longs); w[shorts]=-1.0/len(shorts)
        rnL=Rc.iloc[i+1][longs].dropna(); rnS=Rc.iloc[i+1][shorts].dropna()
        spread=(rnL.mean() if len(rnL) else 0.0) - (rnS.mean() if len(rnS) else 0.0)
        wa,pa=w.align(prev,fill_value=0.0); turn=(wa-pa).abs().sum()
        rows.append((spread, turn, 1.0)); idx.append(months[i+1]); prev=w
    df=pd.DataFrame(rows,index=pd.PeriodIndex(idx,freq="M"),columns=["gross","turn","shortnotional"])
    return df

def net_returns(df, borrow_annual):
    tx=TXBPS*df["turn"]; borrow=(borrow_annual/12.0)*df["shortnotional"]
    return df["gross"]-tx-borrow

def volscale(p,target=0.10,w=6,cap=3.0):
    vol=p.rolling(w).std().shift(1)*np.sqrt(12)
    sc=(target/vol).clip(upper=cap).replace([np.inf,-np.inf],np.nan).fillna(0.0); return p*sc, sc

def met(r):
    r=r.dropna(); eq=(1+r).cumprod(); yrs=len(r)/12
    return dict(cagr=eq.iloc[-1]**(1/yrs)-1, dd=(eq/eq.cummax()-1).min(),
                sh=(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan,
                worst=r.min(), skew=float(((r-r.mean())**3).mean()/r.std()**3),
                kurt=float(((r-r.mean())**4).mean()/r.std()**4-3),
                corr=float(r.corr(mkt.reindex(r.index))))
def show(name,r):
    f=met(r); cut=r.dropna().index[int(len(r.dropna())*0.6)]; o=met(r.loc[cut:])
    print(f"{name:34s} FULL cagr{f['cagr']*100:5.1f}% dd{f['dd']*100:6.1f}% Sh{f['sh']:5.2f} corrSPY{f['corr']:+.2f} worstMo{f['worst']*100:5.1f}% skew{f['skew']:+.2f} | OOS Sh{o['sh']:5.2f} cagr{o['cagr']*100:5.1f}% dd{o['dd']*100:6.1f}%")

df=ls_returns()
print("LONG-SHORT RESIDUAL MOMENTUM (market-neutral, survivorship-free). OOS=last 40%.")
print(f"avg monthly turnover {df['turn'].mean():.2f} (gross) | months {len(df)}")
print("-"*150)
print(">>> borrow-fee sensitivity (transaction cost 5bps both legs always):")
for b in (0.0,0.01,0.03,0.05):
    show(f"  borrow {b*100:.0f}%/yr", net_returns(df,b))
print(">>> vol-scaled (10% target) at 3%/yr borrow [Barroso - should help L/S]:")
vs,sc=volscale(net_returns(df,0.03)); show("  L/S residual + vol-scaled", vs)
print(f"     avg leverage {sc.mean():.2f}x (cap 3x)")
# SPY reference
show("SPY buy&hold (context)", mkt.reindex(df.index).fillna(0))
