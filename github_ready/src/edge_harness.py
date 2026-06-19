"""
edge_harness.py — the ONE front door for testing a strategy for a real edge.

THE GOAL this enforces:
  Find a strategy with a real, cost-surviving edge that beats SPY on BOTH return AND drawdown,
  out-of-sample. Grow it later by breadth + risk-calibrated sizing, NEVER by cranking frequency.

You write ONE function:  signal_fn(df) -> pd.Series of desired position in {-1,0,1} at each bar,
decided using ONLY data up to and including that bar (no look-ahead). The harness handles the rest:
  - delays fills one bar (signal t -> position t+1), so no look-ahead can sneak in
  - builds an equal-weight portfolio across the universe (breadth-native)
  - charges realistic costs on turnover, with a 0/5/10 bps sensitivity ladder
  - splits in-sample vs out-of-sample
  - benchmarks vs SPY buy & hold on BOTH return (CAGR) and max drawdown
  - returns a PASS/FAIL verdict

Why this shape: we proved that indicator-combo strategies on liquid names have ~0 edge, that
frequency multiplies cost not profit, and that the only honest verdict is "beats SPY on both axes
after costs, out-of-sample." This harness makes that verdict cheap to compute and impossible to fake.
"""
from __future__ import annotations
import numpy as np, pandas as pd

TRADING_DAYS = 252

# ----------------------------- metrics -----------------------------
def _metrics(equity, ret):
    eq = equity.dropna()
    if len(eq) < 5:
        return dict(cagr=np.nan, maxdd=np.nan, calmar=np.nan, sharpe=np.nan, total=np.nan, years=0)
    years = len(eq) / TRADING_DAYS
    total = eq.iloc[-1] / eq.iloc[0] - 1.0
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1.0 / years) - 1.0 if years > 0 else np.nan
    dd = (eq / eq.cummax() - 1.0).min()
    vol = ret.std(ddof=0) * np.sqrt(TRADING_DAYS)
    sharpe = (ret.mean() * TRADING_DAYS) / vol if vol > 0 else np.nan
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return dict(cagr=cagr, maxdd=dd, calmar=calmar, sharpe=sharpe, total=total, years=years)

def _portfolio_returns(signal_fn, price_data, cost_bps):
    """Equal-weight across symbols; long/flat/short per signal; fills delayed 1 bar."""
    sleeves = {}
    trades = 0
    expo_frames = []
    for sym, df in price_data.items():
        sig = signal_fn(df).reindex(df.index).fillna(0.0).clip(-1, 1)
        realized = sig.shift(1).fillna(0.0)              # NO look-ahead: act next bar
        ret = df["close"].pct_change(fill_method=None).fillna(0.0)
        turn = realized.diff().abs().fillna(realized.abs())
        cost = (cost_bps / 1e4) * turn
        sleeves[sym] = realized * ret - cost
        expo_frames.append(realized.rename(sym))
        trades += int((realized.diff().abs() > 0).sum())
    net = pd.DataFrame(sleeves).dropna(how="all")
    port = net.mean(axis=1)
    expo = pd.concat(expo_frames, axis=1).reindex(net.index).fillna(0.0).abs().mean(axis=1)
    return port, trades, expo

def _spy_benchmark(spy_close, index):
    c = spy_close.reindex(index).dropna()
    ret = c.pct_change(fill_method=None).fillna(0.0)
    return _metrics((1 + ret).cumprod(), ret)

# ----------------------------- the gate -----------------------------
def evaluate(signal_fn, price_data, spy_close, *, name="candidate",
             cost_bps_ladder=(0.0, 5.0, 10.0), realistic_cost_bps=5.0,
             oos_frac=0.4, verbose=True):
    """
    Returns a verdict dict. PASS requires ALL of:
      (1) pre-cost edge exists:  full-sample CAGR at 0 bps  >  SPY CAGR
      (2) out-of-sample, at realistic cost: portfolio CAGR > SPY CAGR
      (3) out-of-sample, at realistic cost: portfolio |maxDD| < SPY |maxDD|
    Rationale: (1) is the cheap zero-cost pre-filter — no edge before costs => dead on arrival.
               (2)+(3) are THE GOAL: beat SPY on both axes after costs, out-of-sample.
    """
    out = {"name": name, "ladder": {}, "checks": {}}
    # full-sample across cost ladder
    for cb in cost_bps_ladder:
        port, trades, expo = _portfolio_returns(signal_fn, price_data, cb)
        m = _metrics((1 + port).cumprod(), port)
        m["trades"] = trades; m["avg_exposure"] = float(expo.mean())
        out["ladder"][cb] = m
    idx_full = (1 + _portfolio_returns(signal_fn, price_data, 0.0)[0]).cumprod().index
    spy_full = _spy_benchmark(spy_close, idx_full)
    out["spy_full"] = spy_full

    # out-of-sample tail
    cut = idx_full[int(len(idx_full) * (1 - oos_frac))]
    port_oos, _, _ = _portfolio_returns(signal_fn, price_data, realistic_cost_bps)
    port_oos = port_oos.loc[cut:]
    m_oos = _metrics((1 + port_oos).cumprod(), port_oos)
    spy_oos = _spy_benchmark(spy_close, port_oos.index)
    out["oos"] = m_oos; out["spy_oos"] = spy_oos; out["oos_cut"] = str(cut)

    pre = out["ladder"][0.0]
    c1 = (pre["cagr"] > spy_full["cagr"])                                  # zero-cost edge
    c2 = (m_oos["cagr"] > spy_oos["cagr"])                                 # OOS beats SPY return
    c3 = (abs(m_oos["maxdd"]) < abs(spy_oos["maxdd"]))                     # OOS shallower drawdown
    out["checks"] = {"zero_cost_edge": bool(c1), "oos_beats_return": bool(c2), "oos_beats_drawdown": bool(c3)}
    out["verdict"] = "PASS" if (c1 and c2 and c3) else "FAIL"

    if verbose:
        _print_report(out, cost_bps_ladder, realistic_cost_bps)
    return out

def _pf(x): return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:.2f}%"
def _r2(x): return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.2f}"

def _print_report(out, ladder, rc):
    print("="*72); print(f"EDGE VERDICT: {out['name']}"); print("="*72)
    sf = out["spy_full"]
    print(f"SPY buy&hold (full): CAGR {_pf(sf['cagr'])}  maxDD {_pf(sf['maxdd'])}  Calmar {_r2(sf['calmar'])}\n")
    print(f"{'cost/side':>10}{'CAGR':>9}{'maxDD':>9}{'Calmar':>8}{'Sharpe':>8}{'trades':>8}{'expo':>7}")
    for cb in ladder:
        m = out["ladder"][cb]
        print(f"{cb:>8.0f}bp{_pf(m['cagr']):>9}{_pf(m['maxdd']):>9}{_r2(m['calmar']):>8}{_r2(m['sharpe']):>8}{m['trades']:>8}{_pf(m['avg_exposure']):>7}")
    print(f"\nOUT-OF-SAMPLE (from {out['oos_cut'][:10]}, {rc:.0f}bps):")
    mo, so = out["oos"], out["spy_oos"]
    print(f"  strategy: CAGR {_pf(mo['cagr'])}  maxDD {_pf(mo['maxdd'])}")
    print(f"  SPY     : CAGR {_pf(so['cagr'])}  maxDD {_pf(so['maxdd'])}")
    ch = out["checks"]
    print("\nGATE:")
    print(f"  [{'x' if ch['zero_cost_edge'] else ' '}] zero-cost edge (beats SPY CAGR at 0 bps)")
    print(f"  [{'x' if ch['oos_beats_return'] else ' '}] OOS beats SPY return (at {rc:.0f}bps)")
    print(f"  [{'x' if ch['oos_beats_drawdown'] else ' '}] OOS beats SPY drawdown (at {rc:.0f}bps)")
    print(f"\n>>> {out['verdict']} <<<\n")


# ============================ CROSS-SECTIONAL (PANEL) MODE ============================
# For strategies that rank symbols AGAINST EACH OTHER (cross-sectional momentum, value, etc.).
# You provide panel_signal_fn(closes_df) -> weights_df (index=dates, cols=symbols), target
# portfolio weights decided using ONLY past data at each row. The harness delays execution one
# bar (weights.shift(1)) so no look-ahead, charges cost on turnover, and runs the SPY both-axes gate.

def _panel_portfolio(weights, rets, cost_bps):
    held = weights.shift(1).fillna(0.0)                       # decided at t -> held during t+1
    turnover = held.diff().abs().sum(axis=1).fillna(held.abs().sum(axis=1))
    gross = (held * rets).sum(axis=1)
    net = gross - (cost_bps / 1e4) * turnover
    avg_expo = held.abs().sum(axis=1)
    n_trades = int((held.diff().abs().sum(axis=1) > 1e-9).sum())   # rebalance events
    return net, n_trades, avg_expo

def evaluate_panel(panel_signal_fn, price_data, spy_close, *, name="candidate",
                   cost_bps_ladder=(0.0, 5.0, 10.0), realistic_cost_bps=5.0,
                   oos_frac=0.4, verbose=True):
    closes = pd.DataFrame({s: df["close"] for s, df in price_data.items()}).sort_index()
    rets = closes.pct_change(fill_method=None).fillna(0.0)
    weights = panel_signal_fn(closes).reindex(closes.index).reindex(columns=closes.columns).fillna(0.0)

    out = {"name": name, "ladder": {}, "checks": {}}
    for cb in cost_bps_ladder:
        net, ntr, expo = _panel_portfolio(weights, rets, cb)
        m = _metrics((1 + net).cumprod(), net)
        m["trades"] = ntr; m["avg_exposure"] = float(expo.mean())
        out["ladder"][cb] = m
    net0, _, _ = _panel_portfolio(weights, rets, 0.0)
    idx_full = (1 + net0).cumprod().index
    out["spy_full"] = _spy_benchmark(spy_close, idx_full)

    cut = idx_full[int(len(idx_full) * (1 - oos_frac))]
    net_rc, _, _ = _panel_portfolio(weights, rets, realistic_cost_bps)
    net_oos = net_rc.loc[cut:]
    out["oos"] = _metrics((1 + net_oos).cumprod(), net_oos)
    out["spy_oos"] = _spy_benchmark(spy_close, net_oos.index)
    out["oos_cut"] = str(cut)

    pre = out["ladder"][0.0]
    c1 = pre["cagr"] > out["spy_full"]["cagr"]
    c2 = out["oos"]["cagr"] > out["spy_oos"]["cagr"]
    c3 = abs(out["oos"]["maxdd"]) < abs(out["spy_oos"]["maxdd"])
    out["checks"] = {"zero_cost_edge": bool(c1), "oos_beats_return": bool(c2), "oos_beats_drawdown": bool(c3)}
    out["verdict"] = "PASS" if (c1 and c2 and c3) else "FAIL"
    if verbose:
        _print_report(out, cost_bps_ladder, realistic_cost_bps)
    return out
