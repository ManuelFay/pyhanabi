"""Random strategy adapter."""

from .base import LegacyAdapterStrategy


class RandomStrategy(LegacyAdapterStrategy):
    """Baseline random strategy that samples from valid actions."""

    # Delegates to the legacy `Player` implementation in `hanabi.py`.
    legacy_name = "Player"

