# Human strategy design docs

This directory stores strategy principles written in natural language.

Workflow:
1. Add a new `*.md` principles file here (human-authored).
2. Run `scripts/generate_strategy_from_principles.py` to synthesize a strategy implementation.
3. Register the generated strategy alias in `strategies/__init__.py`.
4. Run `scripts/human_strategy_leaderboard.py --games 200` to score self-play performance.

The evaluation leaderboard reports:
- mean score over `N` runs,
- perfect-game count (score == 25),
- perfect-game rate.

`manifest.json` maps design docs to generated strategy aliases and code files.

Current examples:
- `human-prior` (prior-style principles),
- `human-single-hint` (single-card immediate-play hints, else oldest discard).

## Pull-request CI automation

For PRs that change `human_strategies/*_principles.md`, GitHub Actions will:
- generate strategy code from each new principles markdown using `OPENAI_API_KEY`,
- register new strategy mappings in `human_strategies/manifest.json` and `strategies/__init__.py`,
- run `scripts/human_strategy_leaderboard.py --games 200`,
- commit generated artifacts back to the PR branch.

