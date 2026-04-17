"""Strategy package with one strategy implementation per module."""

from .full_strategy import SelfIntentionalPlayer
from .fully_intentional_strategy import FullyIntentionalPlayer
from .inner_strategy import InnerStatePlayer
from .intentional_strategy import IntentionalPlayer
from .outer_strategy import OuterStatePlayer
from .random_strategy import Player
from .sample_strategy import SamplingRecognitionPlayer
from .self_strategy import SelfRecognitionPlayer
from .timed_strategy import TimedPlayer


STRATEGY_TYPES = {
    "random": Player,
    "inner": InnerStatePlayer,
    "outer": OuterStatePlayer,
    "self": SelfRecognitionPlayer,
    "intentional": IntentionalPlayer,
    "sample": SamplingRecognitionPlayer,
    "full": SelfIntentionalPlayer,
    "timed": TimedPlayer,
}
