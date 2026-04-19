## Human strategy proposal

> Add your strategy markdown file under `human_strategies/` as `*_principles.md`.
> The CI will generate code, run 200 games, update `docs/human_strategy_leaderboard.md`, and commit generated artifacts back to this PR branch.

### Strategy file path
- `human_strategies/<your_strategy_name>_principles.md`

### Strategy principles markdown (replace this example)
```md
# Basic cooperative strategy

## Goals
- Increase mean score through consistent hints and safe discards.
- Prioritize playing cards with high certainty.

## Rules
1. If you know a card is immediately playable, play it.
2. If partner has an immediately playable card and hints are available, give the most specific hint possible.
3. If no urgent play/hint exists, discard the oldest card that appears safe based on visible information.
4. Avoid risky plays when mistakes are at 2.
5. Prefer preserving 5s and currently critical cards.

## Tie-breakers
- Prefer hinting rank over color when both are equally informative.
- Prefer discarding cards with duplicated visible copies first.
```

### Checklist
- [ ] I added or updated at least one `human_strategies/*_principles.md` file.
- [ ] I understand CI will commit generated code + leaderboard updates to this PR.
