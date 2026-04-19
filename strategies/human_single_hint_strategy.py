"""Generated from human_strategies/single_immediate_hint_strategy_principles.md."""

import random

from .base import AbstractStrategy
from hanabi import Action, HINT_COLOR, HINT_NUMBER, PLAY, DISCARD, get_possible


class HumanSingleImmediateHintStrategy(AbstractStrategy):
    """Hint only for single-card immediate plays; otherwise discard oldest card."""

    SOURCE_DOC = "human_strategies/single_immediate_hint_strategy_principles.md"

    def __init__(self, name, pnr):
        self.name = name
        self.pnr = pnr
        self.explanation = []
        self._pending_hint = None

    @staticmethod
    def _is_immediately_playable(card, board):
        col, num = card
        return board[col][1] + 1 == num

    @staticmethod
    def _single_card_hint_for_target(hand, idx):
        col, num = hand[idx]
        if sum(1 for c, _n in hand if c == col) == 1:
            return Action(HINT_COLOR, col=col)
        if sum(1 for _c, n in hand if n == num) == 1:
            return Action(HINT_NUMBER, num=num)
        return None

    @staticmethod
    def _resolve_pending_single_hint(knowledge_row, pending_hint):
        if pending_hint is None:
            return None
        hint_type, value = pending_hint
        touched = []
        for idx, k in enumerate(knowledge_row):
            possible = get_possible(k)
            if not possible:
                continue
            if hint_type == HINT_COLOR and all(col == value for col, _ in possible):
                touched.append(idx)
            if hint_type == HINT_NUMBER and all(num == value for _, num in possible):
                touched.append(idx)
        if len(touched) == 1:
            return touched[0]
        return None

    def _find_single_immediate_hint(self, nr, hands, board, hints):
        if hints <= 0:
            return None
        for pnr, hand in enumerate(hands):
            if pnr == nr or not hand:
                continue
            for idx, card in enumerate(hand):
                if not self._is_immediately_playable(card, board):
                    continue
                action = self._single_card_hint_for_target(hand, idx)
                if action is not None:
                    action.pnr = pnr
                    return action
        return None

    @staticmethod
    def _is_discard_action(action):
        return action.type == DISCARD

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        hinted_idx = self._resolve_pending_single_hint(knowledge[nr], self._pending_hint)
        self._pending_hint = None
        if hinted_idx is not None:
            play_action = Action(PLAY, cnr=hinted_idx)
            if any(a == play_action for a in valid_actions):
                return play_action

        hint_action = self._find_single_immediate_hint(nr, hands, board, hints)
        if hint_action is not None:
            return hint_action

        discard_actions = [a for a in valid_actions if self._is_discard_action(a)]
        if discard_actions:
            discard_actions.sort(key=lambda a: a.cnr)
            return discard_actions[0]

        return random.choice(valid_actions)

    def inform(self, action, player, game):
        if action.type in (HINT_COLOR, HINT_NUMBER) and action.pnr == self.pnr and player != self.pnr:
            value = action.col if action.type == HINT_COLOR else action.num
            self._pending_hint = (action.type, value)
