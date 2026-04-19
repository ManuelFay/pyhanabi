# Prior strategy principles (human-playable)

- Strategy id: `principled`
- Intended generated module: `strategies/human_principled_strategy.py`
- Intended class: `PrincipledStrategy`

This strategy is specified only by the principles below.

## Core convention

Treat hints as action-directing signals:
1. If you just received a hint, identify cards touched by the hint.
2. If any touched card is certainly playable, play the newest such card.
3. Otherwise, if any touched card is potentially playable, play the newest such card.

"Newest" means highest hand index.

## Turn priority

Use this strict action order:
1. Resolve fresh hint first.
2. If any own card is certainly playable, play one.
3. If possible, hint partner about a currently playable card.
4. If hints are not full, make a guaranteed-safe discard.
5. Otherwise use a risk-ranked discard fallback.

## Hint selection principles

When selecting a hint for a playable partner card:
- Prefer higher-rank playable target cards.
- Prefer narrower hints (fewer touched cards).
- Prefer hints where the intended target is the newest touched card.
- Avoid hints that touch cards that look potentially playable but are actually not playable.

## Discard principles

If discarding:
- Prefer identities already safe to discard.
- Protect critical final copies.
- Protect rank-5 cards.
- If tied, prefer discarding cards with lower play probability.
