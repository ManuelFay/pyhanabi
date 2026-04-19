# Dumb strategy principles (human-playable)

- Strategy id: `dumb-hint`
- Intended generated module: `strategies/dumb_strategy.py`
- Intended class: `DumbStrategy`

This strategy intentionally uses a minimal policy:

1. If you just received a hint, play the card that hint isolated (single touched card). 
2. Otherwise, if hint tokens are available, check partner cards that are immediately playable.
3. Give a hint only if it touches exactly one card in partner hand.
4. If multiple single-card immediate-play hints exist, use the first one found.
5. Otherwise discard the oldest own card (lowest hand index).

No additional conventions or recursive reasoning are used.
