"""Sampling-recognition strategy adapter."""

from .base import LegacyAdapterStrategy


class SampleStrategy(LegacyAdapterStrategy):
    """Sampling-based self-recognition strategy variant."""

    # Delegates to the legacy `SamplingRecognitionPlayer` implementation in `hanabi.py`.
    legacy_name = "SamplingRecognitionPlayer"

