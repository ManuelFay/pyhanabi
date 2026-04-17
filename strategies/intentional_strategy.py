"""Intentional strategy adapter."""

from .base import LegacyAdapterStrategy


class IntentionalStrategy(LegacyAdapterStrategy):
    """Intentional policy that models communicative intent in hints."""

    # Delegates to the legacy `IntentionalPlayer` implementation in `hanabi.py`.
    legacy_name = "IntentionalPlayer"

