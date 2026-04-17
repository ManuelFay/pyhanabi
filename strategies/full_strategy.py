"""Self-intentional strategy adapter."""

from .base import LegacyAdapterStrategy


class FullStrategy(LegacyAdapterStrategy):
    """Full self-intentional strategy with richer belief/intention modeling."""

    # Delegates to the legacy `SelfIntentionalPlayer` implementation in `hanabi.py`.
    legacy_name = "SelfIntentionalPlayer"

