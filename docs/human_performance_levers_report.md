# Hanabi Performance Levers: From Random to Expert

This report summarizes what moved score most in 200-game self-play experiments.

## Quantitative ladder (2-player, 200 games)

- Random baseline: mean **1.220** (P23=0.0%)
- Strong heuristic baseline (`prior`): mean **21.140** (P23=32.0%)
- Best sensitivity variant (`iter1_prior_like`): mean **21.145** (P23=32.5%)
- Net improvement random -> best: **+19.925** points/game.

## Biggest performance levers

1. **Use newest-card hint conventions.**
   - Hints should make one card the obvious immediate play (usually the newest touched card).
2. **Avoid ambiguous hints that touch risky non-playables.**
   - Good teams trade a little speed for reliability; bad hints create chain mistakes.
3. **Prefer narrow, high-precision hints over broad hints.**
   - Single-card or near-single-card hints improve partner action certainty.
4. **Discard with loss aversion for critical cards.**
   - Protect 5s and last copies; discarding them causes irreversible score caps.

## Practical training plan for human players

- **Step 1 (Beginner):** never blind-play; only play when certain.
- **Step 2 (Intermediate):** agree on one hint convention (newest-touched = play).
- **Step 3 (Advanced):** only give hints that your partner can act on next turn.
- **Step 4 (Expert):** track critical-card risk and defend last copies aggressively.
