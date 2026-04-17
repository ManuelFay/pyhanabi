# Prior Strategy Evaluation Notes

## 1) `prior` vs `prior` for 10 games (log-based review)

Command used:
- `python - <<'PY' ... Game([make_player('prior',0), make_player('prior',1)]) ... for seed in range(1,11)`

Observed scores by seed (1..10):
- `[23, 22, 25, 25, 22, 25, 25, 23, 25, 25]`
- Mean: **24.0**

Log-derived mistake counters:
- Misplays (`"and fails."`): **0 total**
- Games with at least one misplay: **0 / 10**
- Discarded 5s: **1 total** (seed 1)
- Hint starvation events (`hints remaining: 0`): **0**

### Remaining mistakes / gaps
Even with no direct misplays, non-perfect games still occur due to **tempo and planning gaps**:
- Seed 1 ended at 23 (`blue:3`) with one `blue 5` discard.
- Seed 2 ended at 22 (`green:2`) after heavy lower-rank green attrition in trash.
- Seed 5 ended at 22 (`white:2`) with white progression stalling.
- Seed 8 ended at 23 (`white:3`) with delayed white completion.

Interpretation:
- The current priors optimize immediate value well, but they do not always pre-build long dependency chains.
- When no immediate playable hint exists, fallback behavior can still lose tempo in endgame setups.

## 2) Strategy priors (what `prior` assumes)

`prior` uses deterministic priors in this order:
1. **Play-first prior:** if a known playable card exists in own hand, play it immediately.
2. **Tempo-hint prior:** if no play exists, hint teammate about currently playable cards (favor specific hints that touch fewer cards).
3. **Safety-discard prior:** if still blocked, discard cheapest card by a risk model (dead cards first, avoid critical cards).
4. **Knowledge fallback prior:** if snapshot data is unavailable, revert to safe knowledge-based play/discard heuristics.

This is intentionally fast (small bounded loops over players/cards) and favors stable throughput over expensive search.

## 3) Self-play means for all non-slow strategies (`--games 20`)

Scope requested: all strategies except `self` and `sample`.

| Strategy | Mean (20 games) | Min | Max | Notes |
|---|---:|---:|---:|---|
| `random` | 1.15 | 0 | 5 | baseline |
| `inner` | 10.95 | 6 | 16 | heuristic |
| `outer` | 13.05 | 9 | 16 | heuristic |
| `intentional` | 12.20 | 8 | 18 | intentional hinting |
| `full` | 16.95 | 10 | 20 | stronger baseline |
| `timed` | 22.05 | 11 | 25 | timing-based signaling |
| `prior` | 24.30 | 22 | 25 | new fast prior strategy |
| `llm` | n/a | n/a | n/a | missing `OPENAI_API_KEY` / `openai` package |
| `fast-llm` | n/a | n/a | n/a | missing `OPENAI_API_KEY` / `openai` package |
| `feedback-llm` | n/a | n/a | n/a | missing `OPENAI_API_KEY` / `openai` package |

Command used:
- `python - <<'PY' ... for s in get_playertypes() if s not in {'self','sample'} ... 20 seeds ... PY`
