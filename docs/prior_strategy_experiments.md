# Prior strategy self-play experiment log

This file tracks iterative `prior` vs `prior` experiments (`python hanabi.py prior prior --games 200`) and whether each change was kept or reverted.

## Current benchmark target
- Goal requested: mean score **>= 23**.
- Best observed so far in these runs: **21.14**.

## Attempt table

| Attempt ID | Change summary | Commit/State | Avg | Stddev | Range | Outcome |
|---|---|---|---:|---:|---|---|
| A0 | Baseline before new edits this round (knowledge-aware hint risk penalty + confidence term + highest guaranteed play rank) | `ee2817f` | 21.14 | 2.385 | 12..25 | Kept baseline |
| A1 | Fundamental protocol split: number hint=play, color hint=save; added `_pick_save_hint`, tracked `_pending_hint_type` to avoid auto-playing on color save clues | working tree experiment | 13.825 | 2.845 | 6..22 | Reverted (major regression) |
| A2 | Number-hint-first scoring (`+18` number / `-12` color) for play prompts | working tree experiment | 20.775 | 2.779 | 7..25 | Reverted (regression) |
| A3 | Reset pending hint state at game start heuristic (`_maybe_reset_for_new_game`) to avoid cross-game state leakage | working tree experiment | 20.615 | 2.614 | 12..25 | Reverted (regression) |
| A4 | Hard filter on low target play probability (`target_play_prob < 0.5`) in `_pick_hint` | working tree experiment | 4.72 | 1.319 | 4..12 | Reverted (collapsed hinting tempo) |
| A5 | Number-only play hints + only number-driven maybe-play responses | working tree experiment | 13.755 | 5.510 | 1..23 | Reverted (major regression) |
| A6 | Reverted to strongest known variant from this line | `ee2817f` | 21.14 | 2.385 | 12..25 | Active |

## Notes
- The strongest stable strategy remains the ambiguity-penalized newest-touch convention baseline (`ee2817f`) at 21.14.
- Attempts to enforce stricter clue semantics (number-only plays or color-save conventions) reduced score materially without a full complementary chop/save protocol.
- The remaining gap to 23 likely needs a deeper coordinated policy: explicit chop movement conventions and/or short-horizon rollout scoring over action sequences rather than single-turn heuristics.
