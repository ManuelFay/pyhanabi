"""Sensitivity-analysis strategy focused on human-like teamwork principles."""

from __future__ import annotations

import random

from .base import AbstractStrategy
from hanabi import (
    COUNTS,
    DISCARD,
    HINT_COLOR,
    HINT_NUMBER,
    PLAY,
    Action,
    discardable,
    get_possible,
    hint_color,
    hint_rank,
    playable,
    potentially_playable,
)


class SensitivityStrategy(AbstractStrategy):
    """Prior-style cooperative strategy with switchable principles."""

    DEFAULT_PRINCIPLES = {
        "newest_touched_convention": True,
        "singleton_hint_preference": True,
        "risky_hint_penalty": True,
        "critical_save_hints": False,
        "loss_averse_discard": True,
    }

    def __init__(self, name, pnr, principles=None):
        self.name = name
        self.pnr = pnr
        self.explanation = []
        self._pending_hint = None
        self.principles = dict(self.DEFAULT_PRINCIPLES)
        if principles:
            self.principles.update(principles)

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

    @staticmethod
    def _touched_indices_from_hand(hand, hint_action):
        touched = []
        for i, (col, num) in enumerate(hand):
            if hint_action.type == HINT_COLOR and col == hint_action.col:
                touched.append(i)
            if hint_action.type == HINT_NUMBER and num == hint_action.num:
                touched.append(i)
        return touched

    @staticmethod
    def _play_probability(possible, board):
        if not possible:
            return 0.0
        playable_cnt = sum(1 for col, num in possible if board[col][1] + 1 == num)
        return playable_cnt / float(len(possible))

    @staticmethod
    def _trash_count(trash):
        counts = {}
        for card in trash:
            counts[card] = counts.get(card, 0) + 1
        return counts

    def _is_critical(self, card, trash, board):
        if board[card[0]][1] >= card[1]:
            return False
        if card[1] == 5:
            return True
        remaining = COUNTS[card[1] - 1] - self._trash_count(trash).get(card, 0)
        return remaining <= 1

    def _pick_hint(self, nr, hands, knowledge, board, hints, trash):
        if hints <= 0:
            return None

        best = None
        for pnr, hand in enumerate(hands):
            if pnr == nr or not hand:
                continue
            for idx, card in enumerate(hand):
                card_playable = self._is_playable(card, board)
                critical_waiting = self._is_critical(card, trash, board) and not card_playable
                if not card_playable and not (self.principles["critical_save_hints"] and critical_waiting):
                    continue

                priority = card[1] * 100 - idx
                if critical_waiting:
                    priority += 140

                for spread, act in self._hint_options_for_card(card, hand):
                    touched = self._touched_indices_from_hand(hand, act)
                    newest_touched = max(touched) if touched else -1
                    possible_after = []
                    for real_card, k in zip(hand, knowledge[pnr]):
                        if act.type == HINT_COLOR:
                            new_k = hint_color(k, act.col, real_card[0] == act.col)
                        else:
                            new_k = hint_rank(k, act.num, real_card[1] == act.num)
                        possible_after.append(get_possible(new_k))

                    risky_touched = [
                        i
                        for i in touched
                        if potentially_playable(possible_after[i], board) and not self._is_playable(hand[i], board)
                    ]
                    target_play_prob = self._play_probability(possible_after[idx], board)

                    score = priority
                    if self.principles["singleton_hint_preference"]:
                        score -= spread * 4
                        if spread == 1:
                            score += 45
                    else:
                        score -= spread

                    if self.principles["newest_touched_convention"]:
                        if newest_touched == idx:
                            score += 30
                        else:
                            score -= 40

                    if self.principles["risky_hint_penalty"] and risky_touched:
                        score -= 420

                    score += int(target_play_prob * 30)

                    if best is None or score > best[0]:
                        act.pnr = pnr
                        best = (score, act)
        return best[1] if best else None

    def _discard_risk(self, possible, board, trash_counts):
        if not possible:
            return 0.0

        total_risk = 0.0
        for col, num in possible:
            if board[col][1] >= num:
                continue
            remaining = COUNTS[num - 1] - trash_counts.get((col, num), 0)
            critical = remaining <= 1
            urgency = max(0, 6 - num)
            risk = urgency * (3.0 if critical else 1.0)
            if num == 5:
                risk += 3.0
            if self.principles["loss_averse_discard"] and critical:
                risk += 3.0
            total_risk += risk
        return total_risk / float(len(possible))

    def _pick_discard(self, possible_cards, board, trash):
        trash_counts = self._trash_count(trash)
        ranked = []
        for idx, poss in enumerate(possible_cards):
            risk = self._discard_risk(poss, board, trash_counts)
            play_p = self._play_probability(poss, board)
            ranked.append((risk, play_p, idx))
        ranked.sort(key=lambda x: (x[0], x[1], -x[2]))
        return ranked[0][2] if ranked else None

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        possible = [get_possible(k) for k in knowledge[nr]]

        touched = self._touched_indices(knowledge[nr], self._pending_hint)
        self._pending_hint = None
        if touched:
            sure_touched = [i for i in touched if playable(possible[i], board)]
            if sure_touched:
                return Action(PLAY, cnr=max(sure_touched))
            maybe_touched = [i for i in touched if potentially_playable(possible[i], board)]
            if maybe_touched:
                return Action(PLAY, cnr=max(maybe_touched))

        guaranteed_plays = [i for i, p in enumerate(possible) if playable(p, board)]
        if guaranteed_plays:
            return Action(PLAY, cnr=max(guaranteed_plays, key=lambda i: max(num for _col, num in possible[i])))

        hint_action = self._pick_hint(nr, hands, knowledge, board, hints, trash)
        if hint_action is not None:
            return hint_action

        discards = [i for i, p in enumerate(possible) if discardable(p, board)]
        if discards and hints < 8:
            return Action(DISCARD, cnr=discards[0])

        discard_idx = self._pick_discard(possible, board, trash)
        if discard_idx is not None:
            return Action(DISCARD, cnr=discard_idx)

        return random.choice(valid_actions)

    def inform(self, action, player, game):
        if action.type in (HINT_COLOR, HINT_NUMBER) and action.pnr == self.pnr and player != self.pnr:
            value = action.col if action.type == HINT_COLOR else action.num
            self._pending_hint = (action.type, value)

    def on_game_end(self, game):
        self._pending_hint = None
