# Single immediate hint strategy principles (human-playable)

- Strategy id: `human-single-hint`
- Intended generated module: `strategies/human_single_hint_strategy.py`
- Intended class: `HumanSingleImmediateHintStrategy`

This strategy intentionally uses a minimal policy:

1. If you just received a hint, play the card that hint isolated (single touched card).
2. Otherwise, if hint tokens are available, check partner cards that are immediately playable.
3. Give a hint only if it touches exactly one card in partner hand.
4. If multiple single-card immediate-play hints exist, use the first one found.
5. Otherwise discard the oldest own card (lowest hand index).

No additional conventions or recursive reasoning are used.
