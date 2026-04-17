"""Strategy package with one strategy per module."""

from .full_strategy import FullStrategy
from .inner_strategy import InnerStrategy
from .intentional_strategy import IntentionalStrategy
from .outer_strategy import OuterStrategy
from .random_strategy import RandomStrategy
from .sample_strategy import SampleStrategy
from .self_strategy import SelfStrategy
from .timed_strategy import TimedStrategy


STRATEGY_TYPES = {
    "random": RandomStrategy,
    "inner": InnerStrategy,
    "outer": OuterStrategy,
    "self": SelfStrategy,
    "intentional": IntentionalStrategy,
    "sample": SampleStrategy,
    "full": FullStrategy,
    "timed": TimedStrategy,
}
