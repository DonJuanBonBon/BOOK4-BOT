# BOOK4-BOT — Next Sleeves to Beat SPY (professional research, 2026-06-18)
GOAL (unchanged): beat SPY on BOTH return AND drawdown, out-of-sample, after costs. We've PROVEN we can
cut drawdown ~in half (book Sharpe ~1.0 = ties SPY). To beat SPY on RETURN we must raise the book's SHARPE
clearly above ~1.0, then apply modest leverage. That requires adding uncorrelated, HIGH-quality sleeves.

## THE PROFESSIONAL BLUEPRINT (what the pros actually weight)
AQR's multi-style "raw composite" allocation (in RISK space):
  ~32% VALUE · 28% MOMENTUM · 15% DEFENSIVE/low-beta · 12% TREND · 10% CARRY · 3% VOLATILITY.
Read that carefully: **VALUE is the single biggest sleeve (32%) and we DON'T have it. Momentum (28%) is
the one we DO have.** We're running the book missing its largest professional component.

## SHARPE + CORRELATION FACTS (from AQR / academic sources)
- Individual alternative-risk-premia Sharpes typically **0.6-0.8**, a few near 1.0 (modest alone -- the
  edge is in COMBINING them).
- **Diversified CARRY across all asset classes: Sharpe ~1.2** (single best standalone we found). Per-asset
  carry ~0.7. Carry = equity dividend yield, bond roll/term-structure, commodity roll, FX rate differential.
- **VALUE and QUALITY have the LOWEST correlations to the other styles** -> they are the BEST diversifiers
  (biggest Sharpe lift when added). Carry/trend/low-beta are more correlated to each other.
- Quality-Minus-Junk (QMJ): significant risk-adjusted returns globally, low correlation -> strong add.

## WHERE WE STAND vs THE BLUEPRINT
| Style (AQR weight) | Have it? | Our sleeve | Status |
|---|---|---|---|
| Value (32%) | NO | -- | **biggest gap; best diversifier; needs data** |
| Momentum (28%) | YES | residual momentum (long) + L/S residual | built |
| Defensive (15%) | YES | low-vol long-only | built (strong, Sharpe 0.97) |
| Trend (12%) | YES | managed-futures trend | built (weak this era) |
| Carry (10%) | NO | -- | high Sharpe (~1.2 diversified); needs data |
| Volatility (3%) | NO | -- | small; tail risk (skip for now) |

## RANKED NEXT SLEEVES (to raise Sharpe -> lever -> beat SPY return)
1. **VALUE** -- biggest blueprint weight AND lowest correlation to our momentum core -> the #1 Sharpe lift.
2. **QUALITY (QMJ)** -- low correlation, real premium, pairs well with value.
3. **CARRY (multi-asset)** -- highest standalone Sharpe (~1.2 diversified); strong independent return source.

## DATA TO GET THESE (the honest gate)
All three need data we don't have from free price files. Two routes:
- **CHEAPEST / PROFESSIONAL & FREE: AQR publishes monthly factor-return datasets** (QMJ, Value [HML-Devil],
  Momentum [UMD], Betting-Against-Beta) free at aqr.com/Insights/Datasets. These are ready-made sleeve
  return streams -> we can TEST a full multi-factor book immediately. CAVEAT: they are LONG-SHORT, levered,
  gross-of-cost academic factors -> an UPPER BOUND on what's achievable, not directly tradeable. Use them to
  PROVE the combination reaches Sharpe > SPY; then build tradeable versions.
- **TRADEABLE VERSION: point-in-time fundamentals** (~$50/mo Sharadar / EODHD fundamentals tier) to build
  value + quality from stock data ourselves, survivorship-free, cost-real. Carry needs richer futures
  (term structure) or AQR's carry series.

## HONEST EXPECTED OUTCOME
A true multi-factor book (value + momentum + quality + carry + defensive + trend), risk-parity weighted and
vol-targeted, has historically reached Sharpe ~1.0-1.3. Levered to SPY's volatility, a Sharpe of ~1.2-1.3
DOES beat SPY's ~1.0 on return at equal risk -- THAT is the realistic path to the goal. But the lift comes
almost entirely from VALUE + QUALITY + CARRY (the pieces we lack), not from re-weighting what we have.
We have squeezed the free-price-data sleeves dry at Sharpe ~1.0.

## PLAN
1. Acquire value/quality(/carry) data: AQR free factor files first (to validate the combination), then
   fundamentals (~$50/mo) for tradeable value+quality.
2. Add as sleeves to the ERC + vol-target book (BOOK4-BOT/engine/multi_strategy_book_v2.py extends cleanly).
3. Test vs SPY on return AND drawdown, OOS, after costs, with $1,000->$X output. Gate unchanged.

## Sources
- Alt risk premia Sharpes/correlations: https://www.aqr.com/-/media/AQR/Documents/Whitepapers/Understand-Alternative-Risk-Premia.pdf ; https://quantpedia.com/which-alternative-risk-premia-strategies-works-as-diversifiers/
- Carry (Sharpe ~1.2 diversified): https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2014/06/Carry.pdf
- Quality Minus Junk: http://www.econ.yale.edu/~shiller/behfin/2013_04-10/asness-frazzini-pedersen.pdf ; https://www.aqr.com/Insights/Datasets/Quality-Minus-Junk-Factors-Monthly
- AQR free factor datasets: https://www.aqr.com/Insights/Datasets
