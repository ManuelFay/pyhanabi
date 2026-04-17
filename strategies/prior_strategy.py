"""PrioritizedIntentionalPlayer strategy implementation."""

import random

from .base import AbstractStrategy
from hanabi import *


class PrioritizedIntentionalPlayer(AbstractStrategy):
    """Fast heuristic player that prioritizes guaranteed value actions."""

    def __init__(self, name, pnr):
        self.name = name
        self.pnr = pnr
        self.explanation = []
        self._hands_snapshot = None

    @staticmethod
    def _is_playable(card, board):
        col, num = card
        return board[col][1] + 1 == num

    @staticmethod
    def _is_dead(card, board):
        col, num = card
        return board[col][1] >= num

    @staticmethod
    def _is_critical(card, trash, board):
        col, num = card
        if board[col][1] >= num:
            return False
        return trash.count(card) >= COUNTS[num - 1] - 1

    @classmethod
    def _discard_cost(cls, card, trash, board):
        col, num = card
        if cls._is_dead(card, board):
            return -1000 + num
        if cls._is_critical(card, trash, board):
            return 1000 + (6 - num) * 10
        distance = max(0, num - (board[col][1] + 1))
        return (6 - num) * 8 + max(0, 3 - distance)

    @staticmethod
    def _hint_options_for_card(card, target_hand):
        col, num = card
        color_hits = sum(1 for c, _n in target_hand if c == col)
        num_hits = sum(1 for _c, n in target_hand if n == num)
        return [
            (color_hits, Action(HINT_COLOR, col=col)),
            (num_hits, Action(HINT_NUMBER, num=num)),
        ]

    def _pick_hint(self, nr, hands, board, hints):
        if hints <= 0:
            return None

        best = None
        for pnr, hand in enumerate(hands):
            if pnr == nr or not hand:
                continue
            for idx, card in enumerate(hand):
                if not self._is_playable(card, board):
                    continue
                priority = card[1] * 100 - idx
                for spread, act in self._hint_options_for_card(card, hand):
                    score = priority - spread
                    if best is None or score > best[0]:
                        act.pnr = pnr
                        best = (score, act)
        if best:
            return best[1]
        return None

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        my_hand = None
        if self._hands_snapshot and nr < len(self._hands_snapshot):
            my_hand = self._hands_snapshot[nr]

        if my_hand:
            playable_idxs = [i for i, card in enumerate(my_hand) if self._is_playable(card, board)]
            if playable_idxs:
                return Action(PLAY, cnr=max(playable_idxs, key=lambda i: my_hand[i][1]))

        hint_action = self._pick_hint(nr, hands, board, hints)
        if hint_action is not None:
            return hint_action

        if my_hand:
            costs = [(self._discard_cost(card, trash, board), i) for i, card in enumerate(my_hand)]
            costs.sort(key=lambda x: x[0])
            chosen_cost, chosen_idx = costs[0]
            if chosen_cost < 900 or hints == 0:
                return Action(DISCARD, cnr=chosen_idx)

        possible = [get_possible(k) for k in knowledge[nr]]
        for i, p in enumerate(possible):
            if playable(p, board):
                return Action(PLAY, cnr=i)
        discards = [i for i, p in enumerate(possible) if discardable(p, board)]
        if discards and hints < 8:
            return Action(DISCARD, cnr=discards[0])

        discard_actions = [Action(DISCARD, cnr=i) for i in range(len(knowledge[nr]))]
        scores = [pretend_discard(a, knowledge[nr], board, trash) for a in discard_actions]
        scores.sort(key=lambda x: -x[1])
        if scores:
            return scores[0][0]

        return random.choice(valid_actions)

    def inform(self, action, player, game):
        self._hands_snapshot = [h[:] for h in game.hands]
