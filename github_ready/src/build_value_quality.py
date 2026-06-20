import numpy as np, pandas as pd, glob
C="data/momentum_cache"
FD="data/BOOK4-BOT/data_fundamentals"
SPYP="data/OPT3-BOT-USE-THIS/data/SPY_daily.csv"
Mc=pd.read_pickle(f"{C}/Mc.pkl"); Mdv=pd.read_pickle(f"{C}/Mdv.pkl")
ART=1.0; WIN=0.5; FLOOR=5.0; TOP=500; Q=0.20; TX=5/1e4; BORROW=0.03
Rc=Mc.pct_change(fill_method=None).mask(Mc.pct_change(fill_method=None).abs()>ART).clip(-WIN,WIN)
months=Mc.index; me=months.to_timestamp(how='end').normalize()

# --- load fundamentals, build point-in-time monthly panels ---
f=pd.concat([pd.read_csv(x) for x in sorted(glob.glob(f"{FD}/fund_shard_*.csv.gz"))],ignore_index=True)
f["period"]=pd.to_datetime(f["period"],errors="coerce")
f["asof"]=pd.to_datetime(f["filing_date"],errors="coerce")
f["asof"]=f["asof"].fillna(f["period"]+pd.Timedelta(days=90))   # conservative lag if no filing date
f=f.dropna(subset=["period","asof"]).sort_values(["ticker","period"])
for c in ["totalStockholderEquity","totalAssets","commonStockSharesOutstanding","shortLongTermDebtTotal",
          "longTermDebt","netIncome","totalRevenue","grossProfit"]:
    f[c]=pd.to_numeric(f[c],errors="coerce")
# TTM flows (rolling 4 quarters by ticker)
g=f.groupby("ticker")
for c in ["netIncome","totalRevenue","grossProfit"]:
    f[c+"_ttm"]=g[c].transform(lambda s: s.rolling(4,min_periods=2).sum())
f["debt"]=f["shortLongTermDebtTotal"].fillna(f["longTermDebt"])
def panel(col):
    p=f.pivot_table(index="asof",columns="ticker",values=col,aggfunc="last").sort_index()
    p=p.reindex(p.index.union(me)).ffill().reindex(me)        # latest filed value as of each month-end
    p.index=months; return p
EQ=panel("totalStockholderEquity"); AST=panel("totalAssets"); SH=panel("commonStockSharesOutstanding")
NI=panel("netIncome_ttm"); GP=panel("grossProfit_ttm"); DEBT=panel("debt")
cols=Mc.columns.intersection(EQ.columns)
Mc2=Mc[cols]; Rc2=Rc[cols]; Mdv2=Mdv[cols]
EQ,AST,SH,NI,GP,DEBT=[x.reindex(columns=cols) for x in (EQ,AST,SH,NI,GP,DEBT)]
mcap=Mc2*SH
BM=EQ/mcap; EP=NI/mcap                       # value: cheap = high B/M, high E/P
GPOA=GP/AST; ROE=NI/EQ; ROA=NI/AST; SAFE=-(DEBT/AST)   # quality
def zrow(df):  # cross-sectional z each month
    return df.sub(df.mean(axis=1),axis=0).div(df.std(axis=1).replace(0,np.nan),axis=0)
VALUE=(zrow(BM)+zrow(EP))/2
QUALITY=(zrow(GPOA)+zrow(ROE)+zrow(ROA)+zrow(SAFE))/4
# residual momentum (for correlation check) -- reuse beta/resid
spy=pd.read_csv(SPYP,parse_dates=["datetime"]).set_index("datetime")["close"]
spym=spy.resample("ME").last().pct_change(); spym.index=spym.index.to_period("M"); mkt=spym.reindex(months)
cov=(Rc.mul(mkt,axis=0)).rolling(36).mean()-Rc.rolling(36).mean().mul(mkt.rolling(36).mean(),axis=0)
beta=cov.div(mkt.rolling(36).var(ddof=0),axis=0); resid=(Rc-beta.mul(mkt,axis=0))[cols]
MOM=resid.rolling(12).sum().shift(1)
def ls(sig):
    prev=pd.Series(dtype=float); out=[]; idx=[]
    for i in range(40,len(months)-1):
        live=(Mc2.iloc[i]>=FLOOR)&Mc2.iloc[i-12].notna()&sig.iloc[i].notna()
        liquid=Mdv2.iloc[i].where(live).dropna().nlargest(TOP).index
        ss=sig.iloc[i][liquid].dropna()
        if len(ss)<20: out.append(0.0); idx.append(months[i+1]); prev=pd.Series(dtype=float); continue
        k=max(1,int(round(len(ss)*Q))); L=ss.nlargest(k).index; S=ss.nsmallest(k).index
        w=pd.Series(0.0,index=cols); w[L]=1/k; w[S]=-1/k
        ret=Rc2.iloc[i+1][L].mean()-Rc2.iloc[i+1][S].mean()
        wa,pa=w.align(prev,fill_value=0.0); turn=(wa-pa).abs().sum()
        out.append((ret if ret==ret else 0)-TX*turn-(BORROW/12)); idx.append(months[i+1]); prev=w
    return pd.Series(out,index=pd.PeriodIndex(idx,freq="M"))
V=ls(VALUE); Qn=ls(QUALITY); M=ls(MOM)
def met(r):
    r=r.dropna(); eq=(1+r).cumprod(); y=len(r)/12
    return eq.iloc[-1]**(1/y)-1,(eq/eq.cummax()-1).min(),(r.mean()*12)/(r.std()*np.sqrt(12)) if r.std()>0 else np.nan,1000*float(eq.iloc[-1])
S=pd.DataFrame({"VALUE":V,"QUALITY":Qn,"MOM_ls":M}).dropna()
print(f"window {S.index.min()} -> {S.index.max()} ({len(S)} mo)")
print("correlation matrix:"); print(S.corr().round(2).to_string()); print()
for c in S.columns:
    cg,dd,sh,end=met(S[c]); print(f"  {c:9s} Sharpe {sh:5.2f}  ann.ret {cg*100:5.1f}%  maxDD {dd*100:5.0f}%  $1,000->${end:,.0f}")
S.to_pickle(f"{C}/sleeves_vq.pkl"); print("\nsaved value/quality/mom_ls sleeve returns -> sleeves_vq.pkl")
