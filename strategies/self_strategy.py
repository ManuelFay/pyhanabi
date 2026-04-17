"""Self-recognition strategy adapter."""

from .base import LegacyAdapterStrategy


class SelfStrategy(LegacyAdapterStrategy):
    """Recursive self-recognition strategy (can be computationally heavy)."""

    # Delegates to the legacy `SelfRecognitionPlayer` implementation in `hanabi.py`.
    legacy_name = "SelfRecognitionPlayer"

