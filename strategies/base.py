"""Abstract strategy contract and shared helpers."""

from abc import ABC, abstractmethod
import copy


class AbstractStrategy(ABC):
    """Base strategy class used by all concrete strategy implementations."""

    def __init__(self, name, pnr):
        self.name = name
        self.pnr = pnr
        self.explanation = []

    @abstractmethod
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        """Return a legal action for the active player index `nr`."""

    def inform(self, action, player, game):
        """Receive transition updates from the engine (optional override)."""

    def get_explanation(self):
        """Return explanation traces for the latest decision(s)."""
        return self.explanation

    @staticmethod
    def get_possible(knowledge, all_colors):
        result = []
        for col in all_colors:
            for i, cnt in enumerate(knowledge[col]):
                if cnt > 0:
                    result.append((col, i + 1))
        return result

    @staticmethod
    def playable(possible, board):
        for (col, nr) in possible:
            if board[col][1] + 1 != nr:
                return False
        return True

    @staticmethod
    def potentially_playable(possible, board):
        for (col, nr) in possible:
            if board[col][1] + 1 == nr:
                return True
        return False

    @staticmethod
    def discardable(possible, board):
        for (col, nr) in possible:
            if board[col][1] < nr:
                return False
        return True

    @staticmethod
    def potentially_discardable(possible, board):
        for (col, nr) in possible:
            if board[col][1] >= nr:
                return True
        return False

    @staticmethod
    def update_knowledge(knowledge, used):
        result = copy.deepcopy(knowledge)
        for r in result:
            for (c, nr) in used:
                r[c][nr - 1] = max(r[c][nr - 1] - used[c, nr], 0)
        return result
