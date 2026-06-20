"""Reference cross-sectional (panel) signal functions for use with edge_harness.evaluate_panel."""
from __future__ import annotations
import numpy as np, pandas as pd

def xsec_momentum(closes, lookback=252, skip=21, top_frac=0.25, rebal=21, long_only=True):
    """
    Cross-sectional momentum: each rebalance, rank names by trailing return over
    [t-lookback, t-skip] (skip the most recent month to dodge short-term reversal), hold the top
    `top_frac` equal-weighted, rebalance every `rebal` trading days. No look-ahead: momentum uses
    only shifted (past) prices; the harness additionally delays execution one bar.
    """
    mom = closes.shift(skip) / closes.shift(lookback) - 1.0      # all inputs are strictly past
    w = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    rebal_dates = closes.index[::rebal]
    for d in rebal_dates:
        row = mom.loc[d].dropna()
        if len(row) < 5:
            continue
        n_top = max(1, int(round(len(row) * top_frac)))
        wd = pd.Series(0.0, index=closes.columns)
        wd[row.nlargest(n_top).index] = 1.0 / n_top
        if not long_only:
            wd[row.nsmallest(n_top).index] = -1.0 / n_top
        w.loc[d] = wd
    return w.ffill().fillna(0.0)

def equal_weight_all(closes):
    """Sanity reference: hold every name equally, every day (== EW buy&hold at 0 cost)."""
    n = closes.shape[1]
    return pd.DataFrame(1.0 / n, index=closes.index, columns=closes.columns)

def xsec_momentum_regime(closes, market, lookback=252, skip=21, top_frac=0.25, rebal=21,
                         sma=200, long_only=True):
    """
    Cross-sectional momentum (same as xsec_momentum) GATED by a market-regime filter:
    hold the momentum book only when `market` (e.g. SPY) is above its `sma`-day moving average,
    otherwise go fully to cash. Daily gate (can de-risk intra-month). No look-ahead: the regime
    at date t uses market close & MA known at t; momentum weights use only past prices; the harness
    additionally delays execution one bar. Rationale: absolute-momentum / trend overlay (Faber,
    Antonacci) to remove bear-market drawdown from a long-only momentum portfolio.
    """
    base = xsec_momentum(closes, lookback, skip, top_frac, rebal, long_only)
    m = market.sort_index()
    sma_line = m.rolling(sma, min_periods=sma).mean()
    regime_full = (m > sma_line).astype(float)                 # computed on FULL series (warm MA)
    regime = regime_full.reindex(closes.index).ffill().fillna(0.0)
    return base.mul(regime, axis=0).fillna(0.0)

def xsec_momentum_weighted(closes, lookback=252, skip=21, top_frac=0.25, rebal=21,
                           scheme="equal", vol_win=21):
    """Cross-sectional momentum with a choice of weighting among the selected winners:
       scheme='equal' (1/n) or scheme='invvol' (inverse trailing-vol, calmer names get more).
       Inverse-vol uses only PAST returns; harness still delays execution one bar."""
    mom = closes.shift(skip) / closes.shift(lookback) - 1.0
    rets = closes.pct_change(fill_method=None)
    invvol = 1.0 / rets.rolling(vol_win).std()
    invvol = invvol.replace([np.inf, -np.inf], np.nan)
    w = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    for d in closes.index[::rebal]:
        row = mom.loc[d].dropna()
        if len(row) < 5:
            continue
        n_top = max(1, int(round(len(row) * top_frac)))
        winners = row.nlargest(n_top).index
        wd = pd.Series(0.0, index=closes.columns)
        if scheme == "invvol":
            iv = invvol.loc[d, winners].dropna()
            if len(iv) and iv.sum() > 0:
                wd[iv.index] = iv / iv.sum()
            else:
                wd[winners] = 1.0 / n_top
        else:
            wd[winners] = 1.0 / n_top
        w.loc[d] = wd
    return w.ffill().fillna(0.0)

def apply_vol_target(weights, closes, target_vol=0.15, win=21, cap=1.0):
    """Scale gross exposure of any weights so the book's trailing realized vol ~ target_vol/yr,
       capped at `cap` (1.0 = no leverage). De-risks automatically when volatility spikes.
       No look-ahead: scale at t uses returns through t (the harness then delays execution 1 bar)."""
    rets = closes.pct_change(fill_method=None).fillna(0.0)
    held = weights.shift(1).fillna(0.0)
    port = (held * rets).sum(axis=1)
    rv = port.rolling(win).std() * np.sqrt(252)
    scale = (target_vol / rv).clip(upper=cap).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return weights.mul(scale, axis=0).fillna(0.0)

def xsec_value_ltr(closes, long_lb=1260, short_lb=252, top_frac=0.25, rebal=21):
    """Price-based VALUE proxy = long-term reversal (De Bondt-Thaler): rank by trailing return
    from ~5yr ago to ~1yr ago [t-long_lb, t-short_lb]; BUY the biggest long-term LOSERS (cheapest),
    equal-weight, monthly. Low-correlated with 12-1 momentum by construction. Price-only proxy for
    value (true value needs fundamentals we don't have). No look-ahead; harness delays execution 1 bar."""
    ltr = closes.shift(short_lb) / closes.shift(long_lb) - 1.0     # 5y-ago to 1y-ago return, all past
    w = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    for d in closes.index[::rebal]:
        row = ltr.loc[d].dropna()
        if len(row) < 5:
            continue
        n = max(1, int(round(len(row) * top_frac)))
        wd = pd.Series(0.0, index=closes.columns)
        wd[row.nsmallest(n).index] = 1.0 / n                       # smallest = biggest losers = "cheap"
        w.loc[d] = wd
    return w.ffill().fillna(0.0)

def cross_asset_trend(closes, lookback=252, skip=21, rebal=21):
    """Cross-asset TIME-SERIES (absolute) momentum / trend-following. For a basket of asset-class
    ETFs (equity, intl, bonds, gold): each rebalance, hold equal-weight ONLY the assets whose 12-1mo
    return is positive ('trending up'); if none qualify, go fully to CASH (0% — de-risk). This is the
    Faber/Antonacci absolute-momentum mechanism. Low-correlated to equity cross-sectional momentum
    because it holds bonds/gold and flees to cash in broad downturns. No look-ahead; harness delays 1 bar."""
    mom = closes.shift(skip) / closes.shift(lookback) - 1.0
    w = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    for d in closes.index[::rebal]:
        row = mom.loc[d].dropna()
        if len(row) < 2:
            continue
        on = row[row > 0].index
        wd = pd.Series(0.0, index=closes.columns)
        if len(on) > 0:
            wd[on] = 1.0 / len(on)
        w.loc[d] = wd          # if none 'on', row stays all-zero -> cash
    return w.ffill().fillna(0.0)

def futures_trend(closes, lookback=252, skip=21, vol_win=63, target_asset_vol=0.40, rebal=21, cap=3.0):
    """Managed-futures TIME-SERIES momentum (LONG/SHORT), inverse-vol scaled (Moskowitz-Ooi-Pedersen).
    For each contract: position sign = sign of trailing 12-1mo return; size = target_asset_vol / its
    trailing realized vol (capped), divided by N so the book runs at a sane leverage. Long/short is the
    point: it shorts downtrending markets, giving counter-cyclical 'crisis alpha'. No look-ahead (mom &
    vol use only past data; harness delays execution 1 bar)."""
    rets = closes.pct_change(fill_method=None)
    mom = closes.shift(skip) / closes.shift(lookback) - 1.0
    sign = mom.apply(np.sign)
    vol = rets.rolling(vol_win).std() * np.sqrt(252)
    raw = sign * (target_asset_vol / vol).clip(upper=cap)
    N = closes.shape[1]
    w_daily = (raw / N)
    w = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    for d in closes.index[::rebal]:
        if d in w_daily.index:
            w.loc[d] = w_daily.loc[d]
    return w.ffill().fillna(0.0)

def rsi2_reversal(closes, rsi_n=2, buy=10, sma_trend=200, sma_exit=5):
    """Connors-style RSI(2) SHORT-TERM REVERSAL (per name, long/flat): enter long when close>SMA200
    (uptrend) AND RSI(2)<buy (short-term oversold); exit when close>SMA5. Operates over DAYS, so it's
    low-correlated to month-scale momentum. Weight = 1/N_universe per active name (natural low exposure).
    No look-ahead; harness delays execution 1 bar."""
    import indicators as I
    cols = closes.columns; N = len(cols)
    out = pd.DataFrame(0.0, index=closes.index, columns=cols)
    for sym in cols:
        c = closes[sym]
        rsi = I.rsi_wilder(c, rsi_n); s200 = I.sma(c, sma_trend); s5 = I.sma(c, sma_exit)
        pos = np.zeros(len(c)); st = 0
        cv=c.values; rv=rsi.values; s2=s200.values; s5v=s5.values
        for i in range(len(c)):
            if np.isnan(s2[i]) or np.isnan(rv[i]) or np.isnan(s5v[i]):
                pos[i]=0; st=0; continue
            if st==0:
                if cv[i] > s2[i] and rv[i] < buy: st=1
            else:
                if cv[i] > s5v[i]: st=0
            pos[i]=st
        out[sym]=pos
    return out / N
