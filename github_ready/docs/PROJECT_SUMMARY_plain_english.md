# What This Project Was, In Plain English
A complete, honest write-up for someone who has never coded or traded. No jargon left unexplained.

## 1. What we set out to do
We wanted to build a computer program (a "trading bot") that grows money by buying and selling stocks
better than the simplest thing anyone can do: just buying the whole US stock market and holding it.
That simple benchmark is called "SPY" (an index fund of the 500 biggest US companies). Beating SPY is
the bar. Almost no professional does it consistently — so this was always a hard goal, on purpose.

## 2. The one rule we never broke: honesty
It is very easy to fool yourself in this game. A test can look amazing on the computer and then lose
real money, because the test cheated without you noticing. So we built everything around one rule:
**a strategy only "counts" if it beats the market honestly** — meaning, after we subtract realistic
trading costs, after we test it on years the strategy never "saw" while being designed, and after we
include the companies that went bankrupt (not just the winners that survived). If it can't beat SPY
under those honest conditions, we throw it out. No exceptions, no wishful thinking.

## 3. What we built (the tools)
- **An honest "idea tester."** Think of it as a lie-detector for trading ideas. You feed it a strategy,
  and it automatically charges realistic costs, tests it on unseen years, and compares it to just
  buying the market — then gives a clear pass or fail. We made this a reusable tool (a "skill") so every
  future idea gets judged the same strict way.
- **A big library of real market data.** Decades of real prices for thousands of companies — including
  ones that later went bankrupt, which most free data quietly leaves out (and that omission is one of
  the biggest ways tests lie to you).
- **A logbook.** Every single test we ran, with its honest result, written down — so we never fool
  ourselves twice or re-test a dead idea.

## 4. What we tested, and what actually happened
Most ideas failed honest testing. That's normal and expected — finding a real edge is rare.
- **100 strategies from the internet** — screened; almost all were folklore with no real edge.
- **Classic chart-pattern strategies** — tested 5 of the best; all lost to simply holding the market.
- **A day-trading bot (fast in-and-out trades)** — no real edge; trading costs ate everything.
- **Momentum (owning stocks that have been going up)** — the ONE idea that passed... at first. But when
  we added back the bankrupt companies (honest data), its big advantage mostly vanished — it ended up
  only roughly tying the market, not beating it.
- **A "multi-strategy book"** — combining several different, unrelated strategies so they balance each
  other out (the one genuinely smart move in investing). This gave us a much *smoother* ride — about
  half the size of the scary drops — but, in real dollars, still did not beat just holding the market.
- **Adding professional factors (value, quality) using paid data ($60/mo)** — this looked like a real
  breakthrough at first: combined the right way it appeared to beat the market. But the final, most
  careful test undid it (see next section).

## 5. The breakthrough that wasn't (the most important lesson)
The multi-factor combination looked like it beat the market — until we charged the cost of "leverage."
Leverage means borrowing money to make your bets bigger. Our combined strategy was very calm (small
swings), so to make real money from it you'd have to borrow heavily to amplify it. The exciting result
quietly assumed that borrowing was free. The moment we charged the real cost of borrowing (using actual
interest rates), the advantage disappeared — it no longer beat the market, and in some years it lost
badly. The "win" was an accounting illusion. Catching that on the computer — instead of with real money —
is exactly why we insisted on honesty the whole way through.

## 6. The honest final verdict
After all of it — momentum, day-trading, multi-strategy books, and paid professional data — **we did not
find a way to make more dollars than simply buying and holding the market, once real-world costs are
charged honestly.** That is not a failure of effort; it is the truthful answer, and most people who chase
this learn it by losing money instead of by careful testing.

What we DID build that is genuinely valuable:
- A rigorous, reusable honesty engine that will judge any future idea fairly.
- A diversified portfolio that, *without borrowing*, delivers roughly market-like returns with about HALF
  the gut-wrenching drops. Less money than the market over a long bull run, but a far calmer, more
  survivable ride. That is a legitimate, sensible thing to own — just not a money machine.

## 7. What you have now, and what you can do with it
- The honest engine + logbook (your durable asset — reuse it for any future idea).
- The calmer diversified portfolio (an option if you value smoother performance over maximum return).
- A clear, evidence-based answer to "can I beat the market with a bot?": realistically, no — and you now
  know that with proof, not hope, which protects your money.
- If you ever revisit it: the only spending that's justified is for a genuine new breakthrough, and the
  binding wall here was structural (the strategy was too calm to lever cheaply), which more data won't fix.

## 8. The single most important takeaway
The most valuable thing we produced is not a strategy — it's the **discipline**. We have a documented,
honest record of what works and what doesn't, and we never deployed an idea whose "edge" was an illusion.
In a field built on overconfident promises, walking away with the truth (and your money intact) is the win.
