"""Outer-state strategy adapter."""

from .base import LegacyAdapterStrategy


class OuterStrategy(LegacyAdapterStrategy):
    """Heuristic strategy that reasons over partner-visible state."""

    # Delegates to the legacy `OuterStatePlayer` implementation in `hanabi.py`.
    legacy_name = "OuterStatePlayer"

