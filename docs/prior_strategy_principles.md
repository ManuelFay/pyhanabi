# Prior strategy principles (human-playable version)

This document describes the exact decision principles implemented by the `prior` strategy (`PrioritizedIntentionalPlayer`) so a human partner could mirror them in self-play.

## Core convention

The strategy treats hints as **action-directing signals**:

1. If you just received a hint, identify all cards touched by that hint.
2. If any touched card is certainly playable, play the **newest** such touched card.
3. Otherwise, if any touched card is potentially playable, play the **newest** such touched card.

"Newest" means highest hand index in this implementation.

---

## Full action order each turn

The strategy uses this strict priority order:

1. **Resolve a fresh hint first** using the convention above.
2. **Guaranteed self play:** if any card is certainly playable from your own knowledge, play one (prefers highest implied rank among guaranteed plays).
3. **Give a play hint** for partner cards that are currently playable, using hint scoring described below.
4. **Guaranteed safe discard** (only when hint tokens are not full).
5. **Risk-ranked discard fallback** if no better move is available.

---

## Hint-selection principles

When choosing a hint for a partner playable card, the strategy scores candidate color/number hints with:

- **Playable-card priority:** higher rank playable cards are prioritized (`rank * 100 - card_index`).
- **Narrowness preference:** hints touching fewer cards are better.
- **Singleton boost:** if hint touches exactly one card, add a bonus.
- **Newest-touch convention alignment:**
  - bonus if intended target is the newest touched card,
  - penalty otherwise.
- **Post-hint ambiguity simulation:**
  - simulate partner knowledge after each candidate hint,
  - identify touched cards that could look potentially playable but are not actually playable,
  - apply a large penalty for such risky hints.
- **Target-play confidence bonus:** add a bonus proportional to target card play probability after hint simulation.

In plain terms: *choose hints that make partner play the right card now, with minimal ambiguity and minimal risk of a wrong "maybe-play" interpretation.*

---

## Discard principles

If discard is needed, risk is estimated per card from current board+trash:

- Discarding already-played identities is effectively safe.
- Discarding identities with only one remaining copy is heavily penalized.
- Lower ranks carry more urgency pressure than higher ranks.
- Rank-5 cards receive additional protection penalty.

Discard choice sorts by:
1. lowest discard risk,
2. then lowest play probability,
3. then a deterministic tie-break.

---

## What this means for a human partner

If you want to partner with this bot effectively:

- Treat hints as immediate action signals.
- After a hint, default to playing the **newest touched** card that appears playable.
- Prefer giving **narrow, unambiguous** hints that isolate one intended playable action.
- Avoid clues that touch extra cards that might be interpreted as playable when they are not.
- Preserve 5s and critical last copies when choosing discards.

---

## Known weakness of this policy family

The policy is mostly one-step tactical. It does not yet implement a deep multi-turn protocol (explicit chop-move semantics / long-horizon conventions), which is likely required to reliably reach very high self-play averages.
