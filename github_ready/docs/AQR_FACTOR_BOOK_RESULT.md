# BOOK4-BOT — AQR multi-factor book test (UPPER BOUND) — 2026-06-19
Free AQR factor data: All-asset Value/Momentum/Carry/Defensive (Century of Factor Premia) + Quality (QMJ USA).
ERC (inverse-vol) + vol-target. CAVEAT: long-short, levered, gross-of-cost ACADEMIC factors = optimistic ceiling.

## THESIS CONFIRMED (positive response)
- Value vs Momentum correlation = -0.55 (the classic negative pairing). Carry/Defensive/Quality ~uncorrelated.
- Per-factor Sharpe: Value 0.60, Momentum 0.69, Carry 0.82, Defensive 0.72, Quality 0.53 (modest alone).
- ERC 5-factor book: **Sharpe 1.48**, corr-to-SPY -0.31 (market-neutral alpha). Combining low-corr factors ~doubled Sharpe.

## HEAD-TO-HEAD 1993-2025 ($1,000 start)
| Strategy | Return | MaxDD | Sharpe | $1,000 -> |
|---|---|---|---|---|
| SPY buy & hold | 10.1% | -38% | 0.72 | $9,766 |
| Factor book levered to SPY vol (~7.5x) | 21.0% | -26% | 1.35 | $89,064 |
| SPY + 50% factor overlay (modest leverage) | 11.5% | -38% | 0.82 | $13,033 |

## HONEST CAVEATS (the $89k is NOT real)
1. Gross of ALL costs (transaction, short borrow, leverage financing). AQR's LIVE funds returned a fraction of paper factors.
2. The $89k needs ~7.5x leverage on a 2%-vol book -> extreme; factor crashes (value 2020, momentum 2009) amplified 7.5x = ruin risk.
3. Factor returns have DECAYED post-publication; 1957-start Sharpe overstates the future.
4. No survivorship-free / cost-real implementation yet.
=> CREDIBLE read = the modest overlay: beats SPY by ~1.4%/yr, higher Sharpe, same DD ($13k vs $9.8k) -- BEFORE costs/decay.

## VERDICT: GREEN LIGHT (qualified)
The multi-factor thesis holds in the idealized test -> justifies building the TRADEABLE version: buy point-in-time
fundamentals (~$50/mo) to build value + quality survivorship-free, combine with our momentum/trend/carry sleeves,
test with REAL costs + the edge-hunter gate. Expect "modestly beat SPY risk-adjusted," not 9x. Engine: engine/aqr_factor_book.py.
