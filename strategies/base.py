"""Abstract strategy contract used by all strategy adapters."""

from abc import ABC, abstractmethod
import importlib


class AbstractStrategy(ABC):
    """Strategy interface expected by the Hanabi game loop."""

    def __init__(self, name, pnr):
        self.name = name
        self.pnr = pnr

    @abstractmethod
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        """Return the next action for the current game state."""

    def inform(self, action, player, game):
        """Receive post-action updates from the game engine."""

    def get_explanation(self):
        """Return explanation traces, if the strategy supports them."""
        return []


class LegacyAdapterStrategy(AbstractStrategy):
    """Adapter around legacy strategy implementations in `hanabi.py`."""

    legacy_name = None

    def __init__(self, name, pnr):
        super().__init__(name, pnr)
        if self.legacy_name is None:
            raise ValueError("legacy_name must be set on adapter strategy")
        # Lazy import prevents circular imports while preserving legacy behavior.
        hanabi_mod = importlib.import_module("hanabi")
        legacy_cls = getattr(hanabi_mod, self.legacy_name)
        self._impl = legacy_cls(name, pnr)

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        return self._impl.get_action(nr, hands, knowledge, trash, played, board, valid_actions, hints)

    def inform(self, action, player, game):
        return self._impl.inform(action, player, game)

    def get_explanation(self):
        return self._impl.get_explanation()
