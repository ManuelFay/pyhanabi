"""Generated from human_strategies/prior_strategy_principles.md.

This strategy intentionally uses only the principles in that design doc.
"""

import random

from .base import AbstractStrategy
from hanabi import (
    Action,
    HINT_COLOR,
    HINT_NUMBER,
    PLAY,
    DISCARD,
    COUNTS,
    get_possible,
    playable,
    potentially_playable,
    discardable,
    hint_color,
    hint_rank,
)


class HumanPriorPrinciplesStrategy(AbstractStrategy):
    """Principle-driven strategy generated from natural language design notes."""

    SOURCE_DOC = "human_strategies/prior_strategy_principles.md"

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
    def _touched_indices(knowledge, pending_hint):
        if pending_hint is None:
            return []
        hint_type, value = pending_hint
        touched = []
        for i, k in enumerate(knowledge):
            possible = get_possible(k)
            if not possible:
                continue
            if hint_type == HINT_COLOR and all(col == value for col, _ in possible):
                touched.append(i)
            if hint_type == HINT_NUMBER and all(num == value for _, num in possible):
                touched.append(i)
        return touched

    @staticmethod
    def _touched_from_action(hand, action):
        touched = []
        for idx, (col, num) in enumerate(hand):
            if action.type == HINT_COLOR and col == action.col:
                touched.append(idx)
            if action.type == HINT_NUMBER and num == action.num:
                touched.append(idx)
        return touched

    @staticmethod
    def _play_probability(possible, board):
        if not possible:
            return 0.0
        playable_count = sum(1 for col, num in possible if board[col][1] + 1 == num)
        return playable_count / float(len(possible))

    @staticmethod
    def _trash_counts(trash):
        counts = {}
        for card in trash:
            counts[card] = counts.get(card, 0) + 1
        return counts

    def _discard_risk(self, possible, board, trash_counts):
        if not possible:
            return 0.0

        risk = 0.0
        for col, num in possible:
            if board[col][1] >= num:
                continue
            remaining = COUNTS[num - 1] - trash_counts.get((col, num), 0)
            if remaining <= 1:
                risk += 12.0
            if num == 5:
                risk += 6.0
            risk += max(0, 6 - num)
        return risk / float(len(possible))

    def _pick_hint(self, nr, hands, knowledge, board, hints):
        if hints <= 0:
            return None

        best = None
        for pnr, hand in enumerate(hands):
            if pnr == nr or not hand:
                continue
            for idx, card in enumerate(hand):
                if not self._is_playable(card, board):
                    continue
                col, num = card
                candidates = [
                    Action(HINT_COLOR, pnr=pnr, col=col),
                    Action(HINT_NUMBER, pnr=pnr, num=num),
                ]
                for action in candidates:
                    touched = self._touched_from_action(hand, action)
                    spread = len(touched)
                    newest = max(touched) if touched else -1

                    risky_touch = False
                    for real_card, k in zip(hand, knowledge[pnr]):
                        if action.type == HINT_COLOR:
                            new_k = hint_color(k, action.col, real_card[0] == action.col)
                        else:
                            new_k = hint_rank(k, action.num, real_card[1] == action.num)
                        poss = get_possible(new_k)
                        if potentially_playable(poss, board) and not self._is_playable(real_card, board):
                            risky_touch = True
                            break

                    score = num * 100 - idx
                    score -= spread * 3
                    if spread == 1:
                        score += 20
                    if newest == idx:
                        score += 20
                    else:
                        score -= 25
                    if risky_touch:
                        score -= 400
                    score += int(self._play_probability([card], board) * 20)

                    if best is None or score > best[0]:
                        best = (score, action)
        return best[1] if best else None

    def _pick_discard(self, possible_cards, board, trash):
        trash_counts = self._trash_counts(trash)
        ranked = []
        for idx, possible in enumerate(possible_cards):
            risk = self._discard_risk(possible, board, trash_counts)
            play_p = self._play_probability(possible, board)
            ranked.append((risk, play_p, idx))
        ranked.sort(key=lambda x: (x[0], x[1], -x[2]))
        return ranked[0][2] if ranked else None

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        possible = [get_possible(k) for k in knowledge[nr]]

        touched = self._touched_indices(knowledge[nr], self._pending_hint)
        self._pending_hint = None
        if touched:
            sure = [i for i in touched if playable(possible[i], board)]
            if sure:
                return Action(PLAY, cnr=max(sure))
            maybe = [i for i in touched if potentially_playable(possible[i], board)]
            if maybe:
                return Action(PLAY, cnr=max(maybe))

        guaranteed = [i for i, p in enumerate(possible) if playable(p, board)]
        if guaranteed:
            return Action(PLAY, cnr=max(guaranteed))

        hint = self._pick_hint(nr, hands, knowledge, board, hints)
        if hint is not None:
            return hint

        safe_discards = [i for i, p in enumerate(possible) if discardable(p, board)]
        if safe_discards and hints < 8:
            return Action(DISCARD, cnr=safe_discards[0])

        fallback = self._pick_discard(possible, board, trash)
        if fallback is not None:
            return Action(DISCARD, cnr=fallback)

        return random.choice(valid_actions)

    def inform(self, action, player, game):
        if action.type in (HINT_COLOR, HINT_NUMBER) and action.pnr == self.pnr and player != self.pnr:
            value = action.col if action.type == HINT_COLOR else action.num
            self._pending_hint = (action.type, value)
