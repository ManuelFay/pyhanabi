"""Strategy package with one strategy implementation per module."""

from .full_strategy import SelfIntentionalPlayer
from .fully_intentional_strategy import FullyIntentionalPlayer
from .inner_strategy import InnerStatePlayer
from .fast_llm_strategy import FastLLMStrategy
from .feedback_llm_strategy import FeedbackLLMStrategy
from .llm_strategy import LLMStrategy
from .intentional_strategy import IntentionalPlayer
from .outer_strategy import OuterStatePlayer
from .random_strategy import Player
from .sample_strategy import SamplingRecognitionPlayer
from .self_strategy import SelfRecognitionPlayer
from .timed_strategy import TimedPlayer
from .prior_strategy import PrioritizedIntentionalPlayer
from .sensitivity_strategy import SensitivityStrategy
from .human_prior_principles_strategy import HumanPriorPrinciplesStrategy
from .human_single_hint_strategy import HumanSingleImmediateHintStrategy
from .human_principled_strategy import HumanPrincipledStrategy


STRATEGY_TYPES = {
    "random": Player,
    "inner": InnerStatePlayer,
    "outer": OuterStatePlayer,
    "self": SelfRecognitionPlayer,
    "intentional": IntentionalPlayer,
    "sample": SamplingRecognitionPlayer,
    "full": SelfIntentionalPlayer,
    "timed": TimedPlayer,
    "llm": LLMStrategy,
    "fast-llm": FastLLMStrategy,
    "feedback-llm": FeedbackLLMStrategy,
    "prior": PrioritizedIntentionalPlayer,
    "sensitivity": SensitivityStrategy,
    "human-prior": HumanPriorPrinciplesStrategy,
    "human-single-hint": HumanSingleImmediateHintStrategy,
    "human-principled": HumanPrincipledStrategy,
}
