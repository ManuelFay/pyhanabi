"""Implementation based on principles in /home/runner/work/pyhanabi/pyhanabi/human_strategies/dumb_principles.md."""

import random

from .base import AbstractStrategy
from hanabi import Action, DISCARD, HINT_COLOR, HINT_NUMBER, PLAY

try:
    from hanabi import COLORNAMES
except Exception:
    COLORNAMES = None


_DESIRED_COLOR_ORDER = ("blue", "green", "red", "white", "yellow")


def _as_lower_text(value):
    return str(value).lower() if value is not None else ""


def _extract_card_color_num(card):
    if card is None:
        return None, None

    if isinstance(card, dict):
        color = card.get("col", card.get("color", card.get("suit")))
        num = card.get("num", card.get("number", card.get("value")))
        if color is not None or num is not None:
            return color, num

    if isinstance(card, (list, tuple)):
        if len(card) >= 2:
            return card[0], card[1]

    for color_key in ("col", "color", "suit"):
        if hasattr(card, color_key):
            color = getattr(card, color_key)
            break
    else:
        color = None

    for num_key in ("num", "number", "value"):
        if hasattr(card, num_key):
            num = getattr(card, num_key)
            break
    else:
        num = None

    return color, num


def _extract_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default


def _board_top_for_color(board, played, color):
    def from_entry(entry):
        if entry is None:
            return None
        if isinstance(entry, int):
            return entry
        if isinstance(entry, dict):
            for key in (color, str(color), _as_lower_text(color)):
                if key in entry:
                    return from_entry(entry[key])
            return None
        if isinstance(entry, (list, tuple)):
            if not entry:
                return 0
            last = entry[-1]
            if isinstance(last, int):
                return last
            _, num = _extract_card_color_num(last)
            if num is not None:
                return _extract_int(num, 0)
            return None
        _, num = _extract_card_color_num(entry)
        if num is not None:
            return _extract_int(num, 0)
        if hasattr(entry, "top"):
            return from_entry(getattr(entry, "top"))
        if hasattr(entry, "cards"):
            cards = getattr(entry, "cards")
            if cards:
                return from_entry(cards[-1])
            return 0
        return None

    if board is not None:
        if isinstance(board, dict):
            for key in (color, str(color), _as_lower_text(color)):
                if key in board:
                    top = from_entry(board[key])
                    if top is not None:
                        return top
        elif isinstance(board, (list, tuple)):
            cidx = _extract_int(color, None)
            if cidx is not None and 0 <= cidx < len(board):
                top = from_entry(board[cidx])
                if top is not None:
                    return top
        else:
            if hasattr(board, "board"):
                top = _board_top_for_color(getattr(board, "board"), played, color)
                if top is not None:
                    return top
            if hasattr(board, "piles"):
                piles = getattr(board, "piles")
                if isinstance(piles, dict):
                    for key in (color, str(color), _as_lower_text(color)):
                        if key in piles:
                            top = from_entry(piles[key])
                            if top is not None:
                                return top
                elif isinstance(piles, (list, tuple)):
                    cidx = _extract_int(color, None)
                    if cidx is not None and 0 <= cidx < len(piles):
                        top = from_entry(piles[cidx])
                        if top is not None:
                            return top

    if played is not None:
        max_num = 0
        for card in played:
            c, n = _extract_card_color_num(card)
            if c == color or _as_lower_text(c) == _as_lower_text(color):
                n = _extract_int(n, None)
                if n is not None and n > max_num:
                    max_num = n
        return max_num

    return 0


def _is_playable(card, board, played):
    color, num = _extract_card_color_num(card)
    num = _extract_int(num, None)
    if color is None or num is None:
        return False
    top = _board_top_for_color(board, played, color)
    top = _extract_int(top, 0)
    return top + 1 == num


def _color_order_key(color):
    name = None
    if isinstance(color, int) and COLORNAMES is not None:
        try:
            if 0 <= color < len(COLORNAMES):
                name = _as_lower_text(COLORNAMES[color])
        except Exception:
            name = None
    if name is None:
        name = _as_lower_text(color)
    if name in _DESIRED_COLOR_ORDER:
        return (0, _DESIRED_COLOR_ORDER.index(name))
    if isinstance(color, int):
        return (1, color)
    return (2, name)


def _find_valid_action(valid_actions, action_type, pnr=None, col=None, num=None, cnr=None):
    probe = Action(action_type, pnr=pnr, col=col, num=num, cnr=cnr)
    for action in valid_actions:
        if action == probe:
            return action
    return None


class HumanDumbStrategy(AbstractStrategy):
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", "dumb-hint")
        pnr = kwargs.pop("pnr", None)

        if len(args) == 1:
            if pnr is None:
                pnr = args[0]
        elif len(args) >= 2:
            name = args[0]
            pnr = args[1]

        super().__init__(name, pnr)
        self._pending_hint = None

    def inform(self, *args, **kwargs):
        payloads = list(args) + [kwargs]
        for payload in payloads:
            if isinstance(payload, Action):
                if payload.type in (HINT_COLOR, HINT_NUMBER) and payload.pnr == self.pnr:
                    if payload.type == HINT_COLOR:
                        self._pending_hint = ("color", payload.col)
                    else:
                        self._pending_hint = ("number", payload.num)
                    return

            if isinstance(payload, dict):
                action = payload.get("action")
                if isinstance(action, Action):
                    if action.type in (HINT_COLOR, HINT_NUMBER) and action.pnr == self.pnr:
                        if action.type == HINT_COLOR:
                            self._pending_hint = ("color", action.col)
                        else:
                            self._pending_hint = ("number", action.num)
                        return

                hint_type = payload.get("type")
                target = payload.get("pnr", payload.get("player", payload.get("target")))
                if target != self.pnr:
                    continue
                if hint_type in (HINT_COLOR, "hint_color", "color", "colour"):
                    if "col" in payload:
                        self._pending_hint = ("color", payload.get("col"))
                        return
                    if "color" in payload:
                        self._pending_hint = ("color", payload.get("color"))
                        return
                if hint_type in (HINT_NUMBER, "hint_number", "number", "num"):
                    if "num" in payload:
                        self._pending_hint = ("number", payload.get("num"))
                        return
                    if "number" in payload:
                        self._pending_hint = ("number", payload.get("number"))
                        return

    def _play_hinted_card(self, hands, valid_actions):
        if self._pending_hint is None:
            return None

        kind, value = self._pending_hint
        my_hand = hands[self.pnr] if hands and 0 <= self.pnr < len(hands) else []
        matches = []

        for idx, card in enumerate(my_hand):
            c, n = _extract_card_color_num(card)
            if kind == "color":
                if c == value or _as_lower_text(c) == _as_lower_text(value):
                    matches.append(idx)
            else:
                if _extract_int(n, None) == _extract_int(value, None):
                    matches.append(idx)

        self._pending_hint = None
        if len(matches) != 1:
            return None

        idx = matches[0]
        if idx < 0 or idx >= len(my_hand):
            return None

        candidate = Action(PLAY, cnr=idx)
        if candidate in valid_actions:
            return candidate
        return candidate

    def _choose_hint(self, nr, hands, board, played, valid_actions):
        if not hands:
            return None

        best_key = None
        best_action = None

        for pnr, hand in enumerate(hands):
            if pnr == nr or not hand:
                continue

            color_counts = {}
            num_counts = {}
            for card in hand:
                c, n = _extract_card_color_num(card)
                color_counts[c] = color_counts.get(c, 0) + 1
                n = _extract_int(n, None)
                num_counts[n] = num_counts.get(n, 0) + 1

            for idx, card in enumerate(hand):
                if not _is_playable(card, board, played):
                    continue

                color, num = _extract_card_color_num(card)
                num = _extract_int(num, None)

                if color_counts.get(color, 0) == 1:
                    action = Action(HINT_COLOR, pnr=pnr, col=color)
                    if action in valid_actions:
                        key = (0, _color_order_key(color), pnr, idx)
                        if best_key is None or key < best_key:
                            best_key = key
                            best_action = action

                if num_counts.get(num, 0) == 1:
                    action = Action(HINT_NUMBER, pnr=pnr, num=num)
                    if action in valid_actions:
                        key = (1, num if num is not None else 999, pnr, idx)
                        if best_key is None or key < best_key:
                            best_key = key
                            best_action = action

        return best_action

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        hinted = self._play_hinted_card(hands, valid_actions)
        if hinted is not None:
            return hinted

        if hints and hints > 0:
            hint_action = self._choose_hint(nr, hands, board, played, valid_actions)
            if hint_action is not None:
                return hint_action

        discard = _find_valid_action(valid_actions, DISCARD, cnr=0)
        if discard is not None:
            return discard

        return random.choice(valid_actions) if valid_actions else Action(DISCARD, cnr=0)
