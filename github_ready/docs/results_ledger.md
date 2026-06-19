# Results Ledger — every strategy tested (append-only; never re-test a dead idea)
Gate = beat SPY on return AND drawdown, out-of-sample, after realistic cost. Zero-cost edge is the pre-filter.

| Date | Strategy | Economic rationale | Pre-cost edge? | 5bps result | OOS vs SPY | VERDICT |
|---|---|---|---|---|---|---|
| 2026-06-17 | 030 SMA+RSI mean-rev+regime | dip-buy in uptrend | weak | CAGR 0.1% (≈flat, ~1% exposure) | no | FAIL |
| 2026-06-17 | 022 PSAR+ADX trend | trend persistence | yes-ish | CAGR 7.3%, DD -13.8% | beats DD only | FAIL (lost to EW buy&hold) |
| 2026-06-17 | 027 EMA pullback | pullback in trend | no | ~0 (10 trades/13yr) | no | FAIL (degenerate) |
| 2026-06-17 | 003 Squeeze momentum | vol expansion | no | CAGR 3.2%, 9027 trades | no | FAIL (cost churn) |
| 2026-06-17 | 066 Keltner breakout | vol breakout | no | CAGR 2.5% | no | FAIL |
| 2026-06-17 | INTRADAY-001 MTF trend-pullback (15m) | trend + pullback timing | NO (+0.015R at 0 cost) | -0.21R/trade | no | FAIL (no raw edge) |

## Next to test (from where_edge_lives.md), highest priority first:
- [ ] Cross-sectional momentum (6-12mo rank, top decile, monthly rebal) on a broad universe
- [ ] Generalized time-series momentum across more sleeves (extend dual-momentum)
- [ ] Post-earnings drift (needs earnings dataset)

## UPDATE 2026-06-17 (later): panel mode built + first cross-sectional test
| Date | Strategy | Economic rationale | Pre-cost edge? | 5bps result (full) | OOS vs SPY | VERDICT |
|---|---|---|---|---|---|---|
| 2026-06-17 | XSec 12-1 momentum, top 25%, monthly (24-name survivor set) | under-reaction / flow; documented anomaly | **YES** | CAGR 17.8% vs SPY 11.2% | return +5pts BUT DD -35.2% vs SPY -33.7% | FAIL (only on drawdown) |

**This is the closest to a real edge so far** — beats SPY on return at every cost level, robust to
costs (low turnover, ~95% invested), positive out-of-sample. Fails the both-axes gate ONLY on
drawdown, because it is unhedged long equity (crashes with the market). CAVEAT: 24-name survivor
universe inflates momentum; provisional until run on the broad datalake (ideally with delisted names).

### Principled next experiment (NOT curve-fitting — drawdown control is independently justified)
Add a market-regime / volatility overlay to the momentum portfolio (we have independent evidence from
the dual-momentum work that a regime gate + vol-target cuts drawdown). Hypothesis: keep the momentum
RETURN premium while pulling drawdown below SPY's → could pass BOTH axes. Test on the broad datalake,
out-of-sample. This grows a real edge via breadth + risk management, never frequency.

## UPDATE 2026-06-17 (later): regime overlay on cross-sectional momentum
| Date | Strategy | Rationale | Pre-cost edge? | 5bps FULL | OOS vs SPY (2018-26) | VERDICT |
|---|---|---|---|---|---|---|
| 2026-06-17 | XSec 12-1 momentum + SPY-200d regime gate | absolute-momentum trend overlay to cut bear-market drawdown (Faber/Antonacci) | YES | CAGR 15.3% / DD -33.8% vs SPY 11.2% / -55.2% (beats BOTH) | CAGR 14.2% vs SPY 15.6%; DD -33.8% vs -33.7% | **FAIL (OOS)** |

**Key lesson:** the gate's spectacular FULL-sample result (beats SPY on both axes, DD -34% vs -55%)
is an IN-SAMPLE artifact — it comes from avoiding the 2008 crash, which sits in the in-sample half.
Out-of-sample (2018-26) the 200-day gate HURT: it cut return from the base momentum's 20.7% down to
14.2% while barely improving drawdown, because that window's only crash (COVID 2020) was a fast V the
SMA filter whipsawed on. A binary trend gate helps in slow bears (2008), hurts in V-crashes + bulls.
Base momentum (no gate) actually had the stronger OOS return (+5pts vs SPY) and missed only narrowly
on drawdown. Caveat compounding all of this: 24-name SURVIVOR universe + single-regime OOS window.
Next rigorous step: broad datalake (less survivorship) before testing further overlays (avoid p-hacking).

## UPDATE 2026-06-17 (datalake run): FIRST PASS — cross-sectional momentum on 65 names
Universe: 65 single stocks (ETFs excluded), 2005-2026, yfinance datalake. OOS = last 40% (~2017-11+).
| Strategy | Pre-cost | 5bps FULL (CAGR/DD) | OOS (CAGR/DD) | SPY OOS | VERDICT |
|---|---|---|---|---|---|
| BASE XSec 12-1 momentum (top 25%, monthly) | edge YES | 18.2% / -49.8% | **24.2% / -29.5%** | 14.9% / -33.7% | **PASS** |
| Momentum + SPY-200d regime gate | edge YES | 15.1% / -24.6% | **15.5% / -24.6%** | 14.9% / -33.7% | **PASS** |

Both beat SPY on BOTH axes out-of-sample. BASE = higher return (+9pts OOS), equity-like drawdown that
still edges SPY, better OOS Calmar (~0.82). GATED = trades ~9pts return for ~5pts shallower drawdown
(OOS Calmar ~0.63; best FULL Calmar 0.61 because it dodged 2008 in-sample). Low turnover (~monthly,
~95%/76% invested) => cost-robust. No-look-ahead verified; equal-weight accounting identity holds on
the new data.

### THE CAVEAT THAT GOVERNS EVERYTHING (do not ignore)
SURVIVORSHIP: the 65 names are TODAY'S survivors (yfinance current tickers). Momentum is materially
INFLATED by this — the biggest winners are in the set by construction, delisted losers are absent.
The real, tradeable edge is SMALLER than these numbers. The anomaly is real (well-documented); the
MAGNITUDE here is optimistic. Before risking money: validate on a POINT-IN-TIME universe (index
membership as it was, including names that later delisted). Also: single OOS window (2017-26 bull +
COVID + 2022). Treat as a strong candidate, not a finished product.

NEXT: (1) point-in-time / survivorship-robust universe; (2) decide return-max (base) vs drawdown-min
(gated) by risk tolerance; (3) optional vol-target as alternative drawdown control. Grow via breadth/
sizing, never frequency.

## UPDATE 2026-06-17 (survivorship-robustness battery on the momentum edge)
Best free pressure-tests of survivorship (true point-in-time/delisted-name data needs paid sources). OOS = last 40%, 5bps.
| Test | What it isolates | OOS result | Reading |
|---|---|---|---|
| 1. Momentum vs EQUAL-WEIGHT of same 65 names | selection skill vs universe survivorship | mom 24.2%/-29.5% vs EW-same 17.8%/-33.2% | momentum SELECTION adds +6.4pts AND lower DD => real skill above the survivor baseline. STRONG |
| 2. Sector-ETF rotation momentum | survivorship-IMMUNE universe (ETFs don't delist) | mom 15.2%/-35.2% vs SPY 14.9%/-33.7% | small positive return edge, fails DD; thin 7-ETF set => low power. Mechanism works but edge is MODEST without single-stock breadth |
| 3. Drop the stars (NVDA,AAPL,AMZN,META,AVGO,NFLX) | edge concentration in famous winners | mom 19.2%/-30.3% vs SPY 14.9%/-33.7% | beats SPY both axes WITHOUT the mega-winners (+4.3pts). Edge is BROAD, not a few names. STRONG |

VERDICT: the momentum edge SURVIVES the survivorship pressure tests (Tests 1 & 3 strong) — it is NOT
merely an artifact of holding today's winners. BUT the magnitude is inflated: genuine selection alpha
over the survivor baseline is ~6pts OOS (Test 1), and on a clean survivorship-free universe the edge is
small (Test 2). RESIDUAL bias still unaddressed: delisted names (a momentum buy that went to zero is
absent from our data). Only paid point-in-time data fixes that. Treat as a REAL but smaller-than-shown
edge; base single-stock momentum is the working candidate.

## UPDATE 2026-06-17 (refinement: risk-management variants, NOT return-tuning)
Pre-committed, theory-justified variants (no param grid-search). All beat SPY both axes OOS.
| Variant | OOS return | OOS drawdown | OOS Calmar | Note |
|---|---|---|---|---|
| V0 base equal-weight | 24.2% | -29.5% | 0.82 | max return |
| V1 inverse-vol weighting | 21.8% | -29.0% | 0.75 | DROPPED — lowered return, didn't cut DD |
| V2 base + vol-target 15% | 16.2% | **-16.9%** | **0.96** | KEEP — drawdown ~halved, still beats SPY |
| V3 invvol + vol-target | 16.1% | -16.4% | 0.98 | invvol adds nothing over V2 |

DECISION: vol-targeting (V2) is the legitimate refinement for "minimize losses" — drawdown nearly
halved vs base and vs SPY, Calmar 0.82->0.96, return still > SPY. Inverse-vol weighting dropped (no
help). Raw-return maximization deliberately NOT pursued (would be curve-fitting on survivor data).
Tradeoff is explicit: base = max return / ~30% DD; vol-target = ~16% DD / lower return. Both pass.
Deliverable: ClaudeAlgo\momentum_backtest\ (engine + colored run_backtest.py) reads ..\datalake.

## UPDATE 2026-06-17 (momentum + value blend — REJECTED, instructive)
Window 2010-2026 (value needs 5yr warmup). Value = price proxy (long-term reversal), not fundamentals.
| Strategy | OOS return | OOS drawdown | Calmar | Sharpe | beats SPY r/dd |
|---|---|---|---|---|---|
| Momentum alone | 26.9% | -29.5% | 0.91 | 1.13 | YES / YES |
| Value proxy alone (LT-reversal) | 16.8% | -39.5% | 0.42 | 0.84 | YES / NO |
| Blend 50/50 | 22.2% | -34.1% | 0.65 | 1.07 | YES / NO |

KEY FINDING: momentum vs value daily-return correlation = **0.77 (HIGH, not low)**. The textbook
value+momentum diversification benefit is mostly a LONG-SHORT phenomenon; as LONG-ONLY equity sleeves
both are dominated by shared market beta, so blending gives little diversification — and since the value
proxy is the weaker, deeper-drawdown factor, the blend just DRAGS momentum down (Calmar 0.91->0.65,
flips drawdown gate from PASS to FAIL). VERDICT: blend rejected. Momentum alone (optionally vol-targeted)
remains the best artifact. LESSON: real breadth needs genuinely uncorrelated CROSS-ASSET sleeves
(bonds/commodities/gold/trend — the dual-momentum engine), not a second long-only equity factor. Or
long-short construction (bigger, riskier build) to strip shared beta.

## UPDATE 2026-06-17 (breadth done right: equity-momentum + CROSS-ASSET trend blend)
Cross-asset trend sleeve = abs-momentum on VTI/EFA/EEM/IEF/TLT/AGG/GLD (cash when nothing trends up).
Window 2006-2026. Correlation equity-mom vs cross-asset-trend = **0.53** (vs value blend's 0.77 — diversification IS real this time).
| Strategy | OOS return | OOS drawdown | Calmar | Sharpe | beats SPY r/dd |
|---|---|---|---|---|---|
| Equity momentum alone | 23.8% | -29.5% | 0.81 | 1.06 | YES / YES |
| Cross-asset trend alone | 4.5% | -21.5% | 0.21 | 0.47 | NO / YES |
| Blend 50/50 | 14.2% | -22.4% | 0.63 | 0.94 | NO / YES |

FINDING: diversification is REAL (corr 0.53, blend drawdown 29.5%->22.4%) — the breadth thesis was
directionally right. BUT the cross-asset trend sleeve has a WEAK return in this era (4.5% OOS; 2010s-20s
were a poor stretch for trend-following), so a 50/50 capital split gives up too much return: the blend
falls BELOW SPY on return and is worse risk-adjusted than momentum alone (Calmar 0.63 vs 0.81) and worse
than momentum+vol-target (Calmar ~0.96). VERDICT: 50/50 blend rejected as an improvement. Did NOT tune the
split to force a pass (that would be curve-fitting). 

CONVERGING CONCLUSION across all breadth tests: MOMENTUM + VOL-TARGET remains the best artifact. Value
blend failed (corr too high). Cross-asset blend diversifies but the diversifier's return is too weak to
help at a fair fixed weight. Further real gains need NEW data (point-in-time for true magnitude;
fundamentals for true value; real commodities/managed-futures for a stronger trend sleeve), not more
re-weighting of what we have. The honest realistic strategy is momentum (optionally vol-targeted).

## UPDATE 2026-06-18 (managed-futures trend sleeve + risk-parity combo with equity momentum)
Futures trend = long/short TS-momentum, inverse-vol scaled, on 21 contracts (datalake_futures). Window 2006-2026.
Correlation equity-momentum vs futures-trend = **0.22** (genuinely independent — best breadth yet).
| Strategy | OOS return | OOS drawdown | Calmar | Sharpe | beats SPY r/dd |
|---|---|---|---|---|---|
| Equity momentum (alone) | 23.9% | -29.5% | 0.81 | 1.04 | YES / YES |
| Futures trend (alone, L/S) | 4.7% | -24.0% | 0.20 | 0.43 | NO / YES |
| Risk-parity combo | 11.0% | -16.4% | 0.67 | 0.87 | NO / YES |
| Risk-parity combo + vol-target 12% | 11.6% | -16.1% | 0.72 | 0.98 | NO / YES |

FINDING (nuanced, honest): the diversification is REAL (corr 0.22; combo drawdown HALVED 29.5%->16.4%,
crisis-alpha mechanism works). BUT trend-following's STANDALONE return is weak in this era (Sharpe 0.43;
consistent with real CTA performance 2010-2022). Risk-parity gives EQUAL RISK to both sleeves, so the
weak sleeve drags the combo: combo Sharpe (0.87-0.98) and Calmar (0.67-0.72) are BELOW equity-momentum
alone (1.04 / 0.81), and return falls below SPY. 
KEY LESSON (Grinold): adding ONE independent but LOW-IC sleeve at equal risk lowers risk-adjusted return.
The law rewards MANY independent bets WITH SKILL — not one weak diversifier. The combo is a superior
LOW-DRAWDOWN profile (16% vs 29%) but not higher-return/Sharpe yet.
NEXT: add MORE independent quality sleeves (multi-universe momentum [breadth, data ready]; short-term
reversal via the RSI2 bot; carry from futures) so the book has enough high-Sharpe independent components
that risk-parity stops dragging. Equity momentum (optionally vol-targeted) remains the single best artifact.

## UPDATE 2026-06-18 (4-sleeve breadth: multi-universe momentum + RSI2 reversal added)
Correlation matrix (daily returns): eqMom~multiMom = **0.92** (REDUNDANT - shared equity/momentum beta),
eqMom~futTrend = 0.22 (independent), eqMom~rsi2Rev = 0.58, futTrend~others = 0.22-0.27.
Sleeve Sharpes (OOS): eqMom 1.00 (strong) | futTrend 0.45 | multiMom 0.83 | rsi2Rev 0.58 (all weak/this-era).
| Combination | OOS return | OOS DD | Calmar | Sharpe | vs eqMom-alone |
|---|---|---|---|---|---|
| eqMom ALONE (reference) | 22.7% | -29.5% | 0.77 | 1.00 | — |
| Risk-parity (equal-risk) 4 sleeves | 5.7% | -11.9% | 0.48 | 0.79 | worse (dilutes strong sleeve) |
| Risk-parity + vol-target | 7.6% | -11.9% | 0.64 | 0.89 | worse Sharpe |
| Trailing-Sharpe wt (3 sleeves) raw | 7.9% | -38.0% | 0.21 | 0.57 | much worse (whipsaw) |
| **Trailing-Sharpe wt + vol-target 12%** | 14.0% | **-15.4%** | **0.91** | **1.16** | higher Sharpe/Calmar, LOWER return |

FINDINGS: (1) multi-universe EQUITY momentum is REDUNDANT (corr 0.92) - dropped. (2) Equal-risk combining
DILUTES the one strong sleeve -> lower Sharpe. (3) Only after dropping the redundant sleeve, SKILL-weighting
(trailing-Sharpe), AND vol-targeting did breadth finally beat momentum-alone on RISK-ADJUSTED terms
(Sharpe 1.16 > 1.00, Calmar 0.91 > 0.77, DD halved) - BUT at LOWER raw return (14% vs 23%, just under SPY).
CAVEAT: that win is modest and sensitive to the vol-target overlay; multiple combination rules were tried,
so treat as in-sample-best, needs forward/OOS validation before trust.
THE FRONTIER (honest): max RETURN = momentum alone (23%/-30%); best RISK-ADJUSTED & lowest DD = vol-targeted
skill-weighted combo (Sharpe 1.16, ~14%/-15%). Cannot have both - genuine tradeoff. Stop in-sample
optimization here (further rule-tweaking = p-hacking); next real step is forward validation.

## UPDATE 2026-06-18 (TRUE MAGNITUDE: survivorship-free momentum on full EODHD universe)
20,745-ticker delisted-inclusive universe (2005-2026). DATA WAS DIRTY: max raw monthly "return" = 3.5
BILLION % ; 1,828 returns >+1000% ; even top-500-liquid had 277 glitches (CBE +11113%, CAA +1700% x3).
Naive run gave a fake 1357% CAGR. After cleaning (price>=$5, drop |monthly|>100% as data error [11,696
dropped], winsorize +/-50%, momentum rebuilt from cleaned returns), monthly engine, top-500 liquid, top-quartile:
| Universe (same engine) | OOS CAGR | OOS DD | Sharpe |
|---|---|---|---|
| Survivors-ONLY (biased) | 17.0% | -21.6% | 0.85 |
| **Survivorship-FREE (honest)** | **14.3%** | **-21.7%** | **0.74** |
| SPY (OOS reference) | 15.2% | -23.9% | - |

THE VERDICT: survivorship inflated momentum by ~2.7pts OOS within the same engine; the original 65-name
daily test (24% OOS) was inflated FURTHER by its narrow mega-cap survivor universe. Survivorship-FREE,
broad-universe momentum is ~14% OOS -- roughly SPY-COMPARABLE on return (14.3% vs 15.2%), slightly better
on drawdown. The edge is MARGINAL once survivorship is removed -- NOT the 24% headline. This vindicates
the survivorship caveat we flagged throughout. Caveats: cleaning method affects the number (winsorizing
winners may understate momentum slightly); bankrupt-to-zero final returns not fully captured (slightly
optimistic still); monthly vs daily engine differs. Bottom line: real momentum edge here is thin/SPY-like.

## UPDATE 2026-06-18 (Phase-1 intraday futures: overnight-range session rules) — FAIL
Data: ES/NQ 1-min 2019-2026 (Databento, ~1929 sessions). Tested fade (reversal) AND breakout (continuation),
both instruments. 1-3 trades/day. Realistic cost ~1.5 ticks RT. OOS = last 40% of sessions.
| Variant | 0-cost exp | 1.5t exp | OOS @1.5t | Verdict |
|---|---|---|---|---|
| ES fade | -0.46t | - | - | KILL (no edge pre-cost) |
| NQ fade | +0.63t | -0.87t | -1.28t | FAIL (dies on cost + OOS) |
| ES breakout | +1.37t | -0.13t | +0.66t (but IS neg) | FAIL (no robust edge) |
| NQ breakout | +2.70t | +1.20t (full +$16.6k) | **-2.01t (-$11k)** | FAIL (in-sample mirage; OOS loses) |
CONCLUSION: simple session-range price rules on ES/NQ have NO robust, cost-surviving, OOS edge. Breakout
beat fade (consistent with momentum>>reversal everywhere we've tested), and NQ breakout's full-sample
profit was a pure in-sample artifact that reversed out-of-sample. Intraday ES/NQ is HFT-saturated; simple
OHLCV price levels don't clear the bar. NOT tuning to force a pass. Remaining real hypothesis for intraday
futures = the GAMMA/dealer-positioning layer (Phase 2, needs paid GEX data) -- a signal with structural
rationale we have NOT yet tested. Otherwise intraday futures looks like a dead end for a retail systematic edge.

## UPDATE 2026-06-18 (momentum ENHANCEMENTS on survivorship-free universe: crash-resistance test)
Monthly engine, cleaned, top-500 liquid, top-quartile. OOS=last 40%.
| Variant | FULL CAGR/DD/Sharpe | OOS CAGR/DD/Sharpe | worstMo | skew | kurt |
|---|---|---|---|---|---|
| PLAIN momentum | 12.3% / -27.2% / 0.72 | 16.2% / -21.7% / 0.82 | -14.5% | -0.13 | 0.4 |
| **RESIDUAL momentum** | **14.4% / -23.3% / 0.90** | **16.3% / -19.1% / 0.91** | -12.7% | -0.13 | 0.2 |
| Plain + vol-scaled (Barroso 12%) | 7.7% / -28.2% / 0.54 | 8.9% / -19.4% / 0.61 | -13.5% | +0.43 | 3.2 |
| Residual + vol-scaled | 8.5% / -26.9% / 0.62 | 9.3% / -20.5% / 0.66 | -13.3% | -0.17 | 1.2 |
| SPY buy&hold | 16.3% / -23.9% / 1.12 | 15.8% / -23.9% / 0.97 | -12.5% | -0.31 | 0.4 |

FINDINGS: (1) RESIDUAL (beta-adjusted) momentum is a GENUINE win - better return, Sharpe, drawdown AND
crash tail than plain momentum; the one enhancement that held up. KEEP. (2) Vol-scaling (Barroso) did NOT
transfer to LONG-ONLY momentum (mostly de-levered 0.84x, hurt return, no DD benefit) - it's a LONG-SHORT
technique (long-only vol is market-beta-dominated). (3) SOBER TRUTH: even residual momentum's OOS Sharpe
(0.91) is BELOW SPY's (0.97); long-only momentum has NO Sharpe edge over SPY, so leverage cannot create a
market-beating profit machine. The documented ~2x-Sharpe + crash-resistance live in MARKET-NEUTRAL
LONG-SHORT residual momentum (short the losers to strip beta) - that is the real next step, and a bigger,
riskier build (shorting, borrow costs, momentum-crash tail). Long-only momentum is capped at ~SPY-comparable.

## UPDATE 2026-06-18 (LONG-SHORT residual momentum, market-neutral) — does NOT reach profit-machine bar
Survivorship-free top-500-liquid, dollar-neutral, long top-quintile / short bottom-quintile of residual
12-1 momentum. Tx cost 5bps both legs + borrow-fee sweep. OOS=last 40%. corr to SPY = -0.29 (genuinely market-neutral).
| Borrow/yr | FULL Sharpe | OOS Sharpe | FULL CAGR |
|---|---|---|---|
| 0% (fantasy) | 0.79 | 0.84 | 11.9% |
| 1% | 0.73 | 0.78 | 10.8% |
| 3% (realistic) | 0.60 | 0.67 | 8.7% |
| 5% (hard-to-borrow losers) | 0.48 | 0.56 | 6.5% |
| SPY reference | 1.12 | 0.97 | 16.3% |
Vol-scaling (Barroso) again de-levered (0.82x), cut DD to -19.8% but did NOT raise Sharpe.

DEFINITIVE VERDICT: even market-neutral L/S residual momentum has Sharpe BELOW SPY at any realistic borrow
cost. Leverage cannot create a market-beating machine from a sub-SPY-Sharpe strategy. The academic ~2x-Sharpe
residual/long-short momentum does NOT survive survivorship-free data + real borrow + realistic universe +
monthly rebalance. ACROSS ALL VARIANTS TESTED (plain, residual, vol-scaled, long-short), none beats SPY's
Sharpe honestly. Momentum's real edge is modest/SPY-comparable. There is NO honest leverage path to a
profit machine from momentum with our data/tools. L/S residual is a genuine but LOW-Sharpe market-neutral
DIVERSIFIER (corr -0.29) -- useful only as a small uncorrelated sleeve, not a standalone engine.
BEST KEEPER REMAINS: long-only RESIDUAL momentum (~SPY-comparable, lower drawdown).

## UPDATE 2026-06-18 (MULTI-STRATEGY BOOK: 5 sleeves -> ERC + vol-target)
First pass (5 sleeves) FAILED: naive BAB (mis-specified short-beta bet, -87% DD in tech bull) and monthly
short-term reversal (negative edge, shorts winners in a momentum market, -87% DD) poisoned the ERC book
(Sh 0.38). LESSON re-confirmed: ERC only works if EVERY sleeve has positive expectancy.
Corrected book (dropped reversal; fixed BAB -> LONG-ONLY low-vol). Survivorship-free monthly, OOS=last 40%.
Sleeve correlations: resMom~lowVol 0.78 (both long-equity), LS_resMom corr -0.03/-0.19 (diversifier),
futTrend 0.13-0.30 (diversifier). Only ~2-3 EFFECTIVE independent bets (3 sleeves are long-equity).
| Component | FULL Sh / DD | OOS Sh / CAGR / DD |
|---|---|---|
| resMom_L (long) | 0.85 / -25% | 0.87 / 16.2% / -21% |
| futTrend | 0.32 / -22% | 0.63 / 7.3% / -21% |
| lowVol_L (long) | 0.97 / -18% | 0.68 / 8.7% / -18% |  (strong sleeve - low-vol premium real)
| LS_resMom (mkt-neutral) | 0.56 / -30% | 0.61 / 9.6% / -30% |
| **ERC book** | **0.98 / -11.1%** | **1.01 / 9.5% / -11.1%** |
| ERC book + vol-target(1.3x) | 0.92 / -17% | 0.96 / 11.6% / -13.2% |
| SPY | 1.12 / -24% | 0.97 / 15.8% / -24% |

VERDICT: the book WORKS as risk management -- OOS Sharpe ~1.0 (TIED with SPY's 0.97) at HALF the drawdown
(-11% vs -24%). Best risk-adjusted profile we've built. BUT it does NOT beat SPY on RETURN (9.5-11.6% vs
15.8% OOS) and its Sharpe EDGE over SPY is ~zero (within noise) -> NOT a market-beating machine, because we
only have ~2-3 EFFECTIVE independent bets (most sleeves are long-equity-correlated). To push Sharpe clearly
ABOVE SPY (Dalio needs many uncorrelated streams), the highest-value add is the VALUE sleeve (negatively
correlated to momentum; needs point-in-time fundamentals data) + carry + more genuine diversifiers.
KEEPER: ERC book = SPY-Sharpe at half the drawdown (a genuinely good risk-managed portfolio). Engine saved:
multi-strategy-book/multi_strategy_book_v2.py.

## UPDATE 2026-06-19 (BOOK4-BOT: AQR free multi-factor book = UPPER BOUND test) — POSITIVE (qualified)
5 AQR factors (all-asset Value/Mom/Carry/Defensive + QMJ quality), ERC+vol-target. Value~Mom corr -0.55; book Sharpe
1.48, corr-SPY -0.31. Head-to-head 1993-2025 $1,000: SPY $9,766 (10.1%/-38%/0.72); factor book levered to SPY-vol
$89,064 (21%/-26%/1.35); SPY+50% overlay $13,033 (11.5%/-38%/0.82). CAVEAT: gross/levered(~7.5x)/pre-decay academic
factors -> the $89k is a mirage; credible read is the modest overlay (~+1.4%/yr, higher Sharpe) BEFORE costs. THESIS
CONFIRMED -> green light to build TRADEABLE value+quality (fundamentals ~$50/mo) and test cost-real. Expect modest, not 9x.

## UPDATE 2026-06-19 (BOOK4-BOT tradeable: added VALUE sleeve) — FIRST OOS GATE CLEAR
Value+quality built from EODHD fundamentals (point-in-time, survivorship-free post-2018). QUALITY FAILED
(Sh -0.03) -> dropped. VALUE WON (Sh 0.70 full/1.07 OOS, corr to momentum -0.17). 5-sleeve ERC book OOS Sharpe
1.14 (> SPY 0.97). EQUAL-RISK head-to-head, $1,000: OOS book (2.3x) 19.1%/-18%/$3,403 BEATS SPY 15.8%/-24%/$2,794
on BOTH axes. FULL-sample SPY still wins return (mega-bull). CAVEATS: regime-dependent; leverage-financing on
levered long-only beta NOT fully charged (return margin optimistic, but Sharpe edge is leverage-invariant/real);
L/S borrow+decay risk; fundamentals clean only post-2018. VERDICT: first real OOS both-axes win -- defensible as
"higher Sharpe (1.14) -> beats SPY at equal risk OOS," NOT a guaranteed machine. Engine: BOOK4-BOT/engine/book_with_value.py.

## UPDATE 2026-06-19 (BOOK4-BOT: leverage financing + regime test) — WIN REVERSED, honest
Modeled leverage financing (real BIL T-bill ~1.2%/yr + spread) on the ~2.3-2.8x needed to reach SPY vol.
RESULT: book does NOT beat SPY after financing. OOS rf+0.5%: 14.5%/Sh0.90 vs SPY 15.8%/0.97 (loses return+Sharpe,
DD only). FULL: 1.9-6.7% (loses badly). Unlevered book is 3.8%/5.1%vol -> needs ~2.5x -> financing drag (3.6-7.6%/yr)
eats the edge. The 1.14 OOS Sharpe was UNLEVERED; realized levered+financed = 0.71-0.90 <= SPY. Year-by-year: negative
2009-2020, then +64%/2021 +29%/2022 -> recent value resurgence, not a stable edge. VERDICT: earlier "beats SPY OOS"
was an artifact of uncharged leverage. No robust market-beating edge after honest costs. Genuine deliverable = UNLEVERED
low-drawdown SPY-comparable book. Sharadar would NOT fix it (structural: vol too low -> leverage -> financing). Stop spending.
