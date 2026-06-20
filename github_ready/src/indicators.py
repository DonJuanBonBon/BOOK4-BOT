"""Technical indicators from scratch (no external TA lib). Validated in selftest.py.
No value uses future data. Wilder smoothing where standard."""
from __future__ import annotations
import numpy as np
import pandas as pd

def sma(s, n): return s.rolling(n, min_periods=n).mean()
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rma(s, n):
    """Wilder's running moving average (TradingView ta.rma): SMA seed then recursive alpha=1/n."""
    x = s.to_numpy(dtype=float)
    out = np.full(len(x), np.nan)
    valid = ~np.isnan(x)
    if not valid.any():
        return pd.Series(out, index=s.index)
    first = int(np.argmax(valid))
    seed_pos = first + n - 1
    if seed_pos >= len(x):
        return pd.Series(out, index=s.index)
    out[seed_pos] = np.nanmean(x[first:seed_pos + 1])
    for i in range(seed_pos + 1, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return pd.Series(out, index=s.index)


def rsi_wilder(close, n=14):
    d = close.diff()
    up = d.clip(lower=0.0); dn = (-d).clip(lower=0.0)
    ru = rma(up, n); rd = rma(dn, n)
    rs = ru / rd.replace(0.0, np.nan)
    out = 100.0 - 100.0/(1.0+rs)
    out[rd == 0.0] = 100.0
    return out

def true_range(h, l, c):
    pc = c.shift(1)
    return pd.concat([(h-l), (h-pc).abs(), (l-pc).abs()], axis=1).max(axis=1)

def atr_wilder(h, l, c, n=14):
    return rma(true_range(h,l,c), n)

def adx_wilder(h, l, c, n=14):
    up_move = h.diff(); down_move = -l.diff()
    plus_dm = pd.Series(np.where((up_move>down_move)&(up_move>0), up_move, 0.0), index=h.index)
    minus_dm = pd.Series(np.where((down_move>up_move)&(down_move>0), down_move, 0.0), index=h.index)
    atr = rma(true_range(h,l,c), n)
    plus_di = 100.0*rma(plus_dm, n)/atr
    minus_di = 100.0*rma(minus_dm, n)/atr
    dx = 100.0*(plus_di-minus_di).abs()/(plus_di+minus_di).replace(0.0, np.nan)
    adx = rma(dx, n)
    return pd.DataFrame({"plus_di":plus_di, "minus_di":minus_di, "adx":adx})

def psar(h, l, af_start=0.02, af_step=0.02, af_max=0.2):
    n=len(h); hv=h.values; lv=l.values; sar=np.full(n,np.nan)
    if n<2: return pd.Series(sar, index=h.index)
    bull=True; af=af_start; sar_i=lv[0]; ep=hv[0]; sar[0]=sar_i
    for i in range(1,n):
        prev=sar_i
        sar_i = prev + af*(ep-prev)
        if bull:
            lo2 = lv[i-2] if i>=2 else lv[i-1]
            sar_i = min(sar_i, lv[i-1], lo2)
            if lv[i] < sar_i:
                bull=False; sar_i=ep; ep=lv[i]; af=af_start
            elif hv[i] > ep:
                ep=hv[i]; af=min(af+af_step, af_max)
        else:
            hi2 = hv[i-2] if i>=2 else hv[i-1]
            sar_i = max(sar_i, hv[i-1], hi2)
            if hv[i] > sar_i:
                bull=True; sar_i=ep; ep=hv[i]; af=af_start
            elif lv[i] < ep:
                ep=lv[i]; af=min(af+af_step, af_max)
        sar[i]=sar_i
    return pd.Series(sar, index=h.index)

def stochastic(h, l, c, k=14, k_smooth=3, d=3):
    ll=l.rolling(k, min_periods=k).min(); hh=h.rolling(k, min_periods=k).max()
    raw=100.0*(c-ll)/(hh-ll).replace(0.0, np.nan)
    ks=raw.rolling(k_smooth, min_periods=k_smooth).mean()
    ds=ks.rolling(d, min_periods=d).mean()
    return pd.DataFrame({"k":ks, "d":ds})

def keltner(h, l, c, n=20, mult=1.5, atr_n=None):
    basis=ema(c,n); rng=atr_wilder(h,l,c, atr_n or n)
    return basis, basis+mult*rng, basis-mult*rng

def squeeze_momentum(h, l, c, n=20):
    hh=h.rolling(n, min_periods=n).max(); ll=l.rolling(n, min_periods=n).min()
    detr = c - ((hh+ll)/2.0 + sma(c,n))/2.0
    idx=np.arange(n); xc=idx-idx.mean(); denom=(xc**2).sum(); xlast=idx[-1]-idx.mean()
    def _lr(y):
        yb=y.mean(); slope=(xc*(y-yb)).sum()/denom
        return yb+slope*xlast
    return detr.rolling(n, min_periods=n).apply(_lr, raw=True)
