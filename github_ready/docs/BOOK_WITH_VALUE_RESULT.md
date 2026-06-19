# BOOK4-BOT — tradeable multi-factor book WITH VALUE (2026-06-19) — first OOS gate clear
Built value + quality sleeves from EODHD fundamentals (point-in-time via filing_date, survivorship-free).
QUALITY FAILED (Sharpe -0.03, lost money this window) -> DROPPED. VALUE WON -> ADDED.
VALUE (L/S): Sharpe 0.70 full / 1.07 OOS, corr to momentum -0.17 (the negatively-correlated diversifier we needed).

## 5-sleeve book: resMom_L + futTrend + lowVol_L + LS_resMom + VALUE_ls (ERC + vol-target)
Adding VALUE lifted OOS book Sharpe from ~1.0 (4-sleeve tie) to 1.14 (clear edge over SPY 0.97).

## EQUAL-RISK HEAD-TO-HEAD (book levered to SPY's vol), $1,000 start
| Window | Book ret / DD / Sharpe / $ | SPY ret / DD / Sharpe / $ | Beats SPY return? DD? |
|---|---|---|---|
| OOS (~2016-2026) | 19.1% / -18% / 1.14 / $3,403 (2.3x) | 15.8% / -24% / 0.97 / $2,794 | YES / YES |
| FULL (2009-2026) | 10.2% / -22% / 0.74 / $5,347 (2.8x) | 16.3% / -24% / 1.12 / $13,705 | NO / YES |

## VERDICT: first configuration to beat SPY on BOTH axes OUT-OF-SAMPLE. Genuine, but caveated:
1. REGIME-DEPENDENT: passes OOS (varied 2016+ incl 2020/2022); FAILS full-sample (2009-15 mega-bull favored SPY).
2. LEVERAGE-FINANCING not fully charged in the equal-risk calc (charged borrow on shorts, NOT financing on
   levered long-only beta) -> the 19.1% return margin is optimistic; BUT Sharpe (1.14>0.97) is leverage-invariant
   and real, so a properly-financed lever still beats SPY at equal risk, by a smaller margin.
3. L/S sleeves carry real borrow/decay risk; quality failed; fundamentals survivorship-clean only post-2018.

## NEXT (to harden the win): model leverage financing explicitly; forward/paper-validate; test more regimes;
   consider Sharadar for pre-2018 survivorship-clean fundamentals. The risk-adjusted edge (Sharpe 1.14 OOS) is the
   real, defensible result -- "beats SPY at equal risk OOS," not "guaranteed money machine."

## CORRECTION (2026-06-19) — leverage financing modeled explicitly: the win does NOT survive
Charged real financing (BIL T-bill ~1.2%/yr + spread) on the leverage needed to reach SPY's vol (~2.3-2.8x):
| Window | Book levered+financed | SPY | Beats? |
|---|---|---|---|
| OOS rf+0.5% | ret 14.5% Sh 0.90 | 15.8% / 0.97 | NO return, NO Sharpe (DD only) |
| OOS rf+3% | ret 11.0% Sh 0.71 | 15.8% / 0.97 | NO |
| FULL (any) | 1.9-6.7% | 16.3% | NO (badly) |
The unlevered book earns only 3.8%/yr at 5.1% vol -> needs ~2.5x leverage -> financing drag (3.6-7.6%/yr)
eats the entire edge. The 1.14 OOS Sharpe was UNLEVERED; realized levered+financed Sharpe = 0.71-0.90 (<= SPY 0.97).
REGIME TEST (year-by-year, levered, rf+1.5%): NEGATIVE almost every year 2009-2020, then +64% (2021), +29% (2022),
+22% (2026). The "edge" is a recent value/factor resurgence, NOT a stable repeatable edge.

## FINAL HONEST VERDICT
After honest leverage financing, the multi-factor book does NOT beat SPY on return OR risk-adjusted return in
either window. The earlier "beats SPY OOS" was an artifact of UNCHARGED leverage. The book's only genuine,
durable property remains what we've found all along: a low-drawdown, ~SPY-comparable UNLEVERED portfolio (a
smoother ride), NOT a leveraged market-beater. Sharadar (pre-2018 fundamentals) would NOT fix this -- the binding
constraint is structural (book vol too low -> too much leverage -> financing eats the edge), not data coverage.
RECOMMENDATION: do NOT spend more on data; do NOT deploy leverage. The defensible deliverable is the UNLEVERED
diversified book as a lower-drawdown SPY alternative. Beating SPY in dollars remains unachieved after honest costs.
