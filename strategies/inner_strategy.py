"""Inner-state strategy adapter."""

from .base import LegacyAdapterStrategy


class InnerStrategy(LegacyAdapterStrategy):
    """Heuristic strategy based on local hand-knowledge reasoning."""

    # Delegates to the legacy `InnerStatePlayer` implementation in `hanabi.py`.
    legacy_name = "InnerStatePlayer"

