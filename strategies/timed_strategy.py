"""Timed strategy adapter."""

from .base import LegacyAdapterStrategy


class TimedStrategy(LegacyAdapterStrategy):
    """Time-bounded intentional strategy variant."""

    # Delegates to the legacy `TimedPlayer` implementation in `hanabi.py`.
    legacy_name = "TimedPlayer"

