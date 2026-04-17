"""Rule-compliant PrioritizedIntentionalPlayer strategy implementation."""

import random

from .base import AbstractStrategy
from hanabi import *


class PrioritizedIntentionalPlayer(AbstractStrategy):
    """Fast rule-compliant heuristic strategy (no hidden-hand access)."""

    def __init__(self, name, pnr):
        self.name = name
        self.pnr = pnr
        self.explanation = []
        self._pending_hint = None

    @staticmethod
    def _is_playable(card, board):
        col, num = card
        return board[col][1] + 1 == num

    @staticmethod
    def _hint_options_for_card(card, target_hand):
        col, num = card
        color_hits = sum(1 for c, _n in target_hand if c == col)
        num_hits = sum(1 for _c, n in target_hand if n == num)
        return [
            (color_hits, Action(HINT_COLOR, col=col)),
            (num_hits, Action(HINT_NUMBER, num=num)),
        ]

    @staticmethod
    def _touched_indices(knowledge, pending_hint):
        if pending_hint is None:
            return []
        hint_type, value = pending_hint
        touched = []
        for i, k in enumerate(knowledge):
            possible = get_possible(k)
            if not possible:
                continue
            if hint_type == HINT_COLOR:
                if all(col == value for col, _ in possible):
                    touched.append(i)
            else:
                if all(num == value for _, num in possible):
                    touched.append(i)
        return touched

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
                    # Favor narrow hints to reduce ambiguity under conventions.
                    score = priority - spread * 2
                    if spread == 1:
                        score += 40
                    if best is None or score > best[0]:
                        act.pnr = pnr
                        best = (score, act)
        return best[1] if best else None

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        possible = [get_possible(k) for k in knowledge[nr]]

        # Convention: after receiving a hint, prioritize touched cards that are now certainly playable.
        touched = self._touched_indices(knowledge[nr], self._pending_hint)
        self._pending_hint = None
        if touched:
            sure_touched = [i for i in touched if playable(possible[i], board)]
            if sure_touched:
                return Action(PLAY, cnr=sure_touched[0])
            maybe_touched = [i for i in touched if potentially_playable(possible[i], board)]
            if len(maybe_touched) == 1:
                return Action(PLAY, cnr=maybe_touched[0])

        # Guaranteed play.
        guaranteed_plays = [i for i, p in enumerate(possible) if playable(p, board)]
        if guaranteed_plays:
            return Action(PLAY, cnr=guaranteed_plays[0])

        # High-value hint for a partner's immediately playable card.
        hint_action = self._pick_hint(nr, hands, board, hints)
        if hint_action is not None:
            return hint_action

        # Guaranteed safe discard.
        discards = [i for i, p in enumerate(possible) if discardable(p, board)]
        if discards and hints < 8:
            return Action(DISCARD, cnr=discards[0])

        # Conservative fallback: discard via expected loss ranking.
        discard_actions = [Action(DISCARD, cnr=i) for i in range(len(knowledge[nr]))]
        scores = [pretend_discard(a, knowledge[nr], board, trash) for a in discard_actions]
        scores.sort(key=lambda x: -x[1])
        if scores:
            return scores[0][0]

        return random.choice(valid_actions)

    def inform(self, action, player, game):
        # Rule-compliant: track only public action metadata, never hidden cards.
        if (
            action.type in (HINT_COLOR, HINT_NUMBER)
            and action.pnr == self.pnr
            and player != self.pnr
        ):
            value = action.col if action.type == HINT_COLOR else action.num
            self._pending_hint = (action.type, value)
