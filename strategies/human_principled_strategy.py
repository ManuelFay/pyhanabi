"""Human principled Hanabi strategy.

Source principles: /home/runner/work/pyhanabi/pyhanabi/human_strategies/principled_principles.md
"""

import random

from .base import AbstractStrategy
from hanabi import Action, HINT_COLOR, HINT_NUMBER, PLAY, DISCARD


class HumanPrincipledStrategy(AbstractStrategy):
    SOURCE_DOC = "/home/runner/work/pyhanabi/pyhanabi/human_strategies/principled_principles.md"
    MAX_HINTS = 8

    def __init__(self, name, pnr):
        super().__init__(name, pnr)
        self._fresh_hint = None

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        my_state = self._player_state(knowledge, nr)

        pending_hint = self._fresh_hint if self._fresh_hint is not None and getattr(self._fresh_hint, "pnr", None) == nr else None
        if pending_hint is not None:
            action = self._resolve_fresh_hint(pending_hint, my_state, board, played, valid_actions)
            self._fresh_hint = None
            if action is not None:
                return action
        else:
            self._fresh_hint = None

        action = self._select_own_play(my_state, board, played, valid_actions)
        if action is not None:
            return action

        if hints is not None and hints > 0:
            action = self._select_hint(hands, nr, board, played, valid_actions)
            if action is not None:
                return action

        if hints is not None and hints < self.MAX_HINTS:
            action = self._select_safe_discard(my_state, board, played, valid_actions)
            if action is not None:
                return action

        action = self._select_risky_discard(my_state, hands, trash, played, board, valid_actions)
        if action is not None:
            return action

        return valid_actions[0] if valid_actions else None

    def inform(self, action, player, game):
        if action is None:
            return
        if getattr(action, "type", None) in (HINT_COLOR, HINT_NUMBER) and getattr(action, "pnr", None) == self.pnr:
            self._fresh_hint = action

    def _player_state(self, knowledge, idx):
        if knowledge is None:
            return None
        if isinstance(knowledge, dict):
            if idx in knowledge:
                return knowledge[idx]
            sidx = str(idx)
            if sidx in knowledge:
                return knowledge[sidx]
            if self.pnr in knowledge:
                return knowledge[self.pnr]
            if str(self.pnr) in knowledge:
                return knowledge[str(self.pnr)]
            return None
        if isinstance(knowledge, (list, tuple)):
            if 0 <= idx < len(knowledge):
                return knowledge[idx]
            return None
        return knowledge

    def _looks_like_single_card(self, obj):
        return isinstance(obj, (list, tuple)) and len(obj) >= 2 and not self._is_collection(obj[0]) and not self._is_collection(obj[1])

    def _is_collection(self, obj):
        return isinstance(obj, (list, tuple, set, frozenset))

    def _as_cards(self, state):
        if state is None:
            return []
        if isinstance(state, dict):
            for key in ("cards", "hand", "knowledge", "cards_knowledge"):
                if key in state:
                    return self._as_cards(state[key])
            return [state]
        if hasattr(state, "cards"):
            return self._as_cards(getattr(state, "cards"))
        if hasattr(state, "hand"):
            return self._as_cards(getattr(state, "hand"))
        if isinstance(state, (list, tuple)):
            if self._looks_like_single_card(state):
                return [state]
            return list(state)
        return [state]

    def _normalize_set(self, value):
        if value is None:
            return None
        if isinstance(value, bool):
            return {value}
        if isinstance(value, (list, tuple, set, frozenset)):
            try:
                return set(value)
            except TypeError:
                return set(list(value))
        return {value}

    def _card_color_num(self, card):
        if card is None:
            return None, None
        if isinstance(card, dict):
            color = None
            num = None
            for key in ("color", "col", "suit"):
                if key in card:
                    color = card[key]
                    break
            for key in ("num", "number", "rank"):
                if key in card:
                    num = card[key]
                    break
            return color, num
        if hasattr(card, "col"):
            color = getattr(card, "col")
        elif hasattr(card, "color"):
            color = getattr(card, "color")
        else:
            color = None
        if hasattr(card, "num"):
            num = getattr(card, "num")
        elif hasattr(card, "number"):
            num = getattr(card, "number")
        elif hasattr(card, "rank"):
            num = getattr(card, "rank")
        else:
            num = None
        if color is not None or num is not None:
            return color, num
        if isinstance(card, (list, tuple)) and len(card) >= 2:
            return card[0], card[1]
        return None, None

    def _entry_info(self, entry):
        if entry is None:
            return None, None, None

        colors = None
        nums = None
        touched = None

        if isinstance(entry, dict):
            for key in ("colors", "possible_colors", "color_options"):
                if key in entry and entry[key] is not None:
                    colors = self._normalize_set(entry[key])
                    break
            if colors is None:
                for key in ("color", "col", "known_color", "hint_color"):
                    if key in entry and entry[key] is not None:
                        colors = self._normalize_set(entry[key])
                        break

            for key in ("nums", "numbers", "possible_nums", "num_options"):
                if key in entry and entry[key] is not None:
                    nums = self._normalize_set(entry[key])
                    break
            if nums is None:
                for key in ("num", "number", "rank", "known_num", "known_number"):
                    if key in entry and entry[key] is not None:
                        nums = self._normalize_set(entry[key])
                        break

            for key in ("touched", "hinted", "was_touched", "revealed", "marked"):
                if key in entry:
                    touched = bool(entry[key])
                    break
            return colors, nums, touched

        for attr in ("colors", "possible_colors", "color_options"):
            if hasattr(entry, attr):
                colors = self._normalize_set(getattr(entry, attr))
                break
        if colors is None:
            for attr in ("color", "col", "known_color", "hint_color"):
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    if value is not None:
                        colors = self._normalize_set(value)
                        break

        for attr in ("nums", "numbers", "possible_nums", "num_options"):
            if hasattr(entry, attr):
                nums = self._normalize_set(getattr(entry, attr))
                break
        if nums is None:
            for attr in ("num", "number", "rank", "known_num", "known_number"):
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    if value is not None:
                        nums = self._normalize_set(value)
                        break

        for attr in ("touched", "hinted", "was_touched", "revealed", "marked"):
            if hasattr(entry, attr):
                touched = bool(getattr(entry, attr))
                break

        if colors is None and nums is None and isinstance(entry, (list, tuple)):
            if len(entry) >= 3:
                colors = self._normalize_set(entry[0])
                nums = self._normalize_set(entry[1])
                touched = bool(entry[2]) if entry[2] is not None else None
            elif len(entry) == 2:
                colors = self._normalize_set(entry[0])
                nums = self._normalize_set(entry[1])

        if colors is not None and len(colors) == 0:
            colors = None
        if nums is not None and len(nums) == 0:
            nums = None
        return colors, nums, touched

    def _all_identities(self, entry):
        colors, nums, _ = self._entry_info(entry)
        if not colors or not nums:
            exact_color, exact_num = self._card_color_num(entry)
            if exact_color is None or exact_num is None:
                return []
            return [(exact_color, exact_num)]
        return [(c, n) for c in colors for n in nums]

    def _identity_total_copies(self, num):
        if num == 1:
            return 3
        if num in (2, 3, 4):
            return 2
        if num == 5:
            return 1
        return 1

    def _extract_progress_value(self, raw):
        if raw is None or isinstance(raw, bool):
            return None
        if isinstance(raw, int):
            return raw
        if isinstance(raw, dict):
            for key in ("num", "number", "rank", "value", "top"):
                if key in raw and isinstance(raw[key], int):
                    return raw[key]
            return None
        if isinstance(raw, (list, tuple, set, frozenset)):
            nums = []
            for item in raw:
                if isinstance(item, bool):
                    continue
                if isinstance(item, int):
                    nums.append(item)
                    continue
                _, num = self._card_color_num(item)
                if isinstance(num, int):
                    nums.append(num)
            return max(nums) if nums else None
        return None

    def _container_progress(self, container, color):
        if container is None:
            return None

        if isinstance(container, dict):
            if color in container:
                return container[color]
            sc = str(color)
            if sc in container:
                return container[sc]
            for key, value in container.items():
                if key == color or str(key) == sc:
                    return value
            return None

        if isinstance(container, (list, tuple)):
            if isinstance(color, int) and 0 <= color < len(container):
                return container[color]
            matches = []
            for item in container:
                c, n = self._card_color_num(item)
                if c == color:
                    matches.append(n if n is not None else item)
            if matches:
                return matches if len(matches) > 1 else matches[0]

        if hasattr(container, "get"):
            try:
                if color in container:
                    return container[color]
                sc = str(color)
                if sc in container:
                    return container[sc]
            except Exception:
                pass

        return None

    def _progress_for_color(self, color, board, played):
        raw = self._container_progress(board, color)
        progress = self._extract_progress_value(raw)
        if progress is None:
            raw = self._container_progress(played, color)
            progress = self._extract_progress_value(raw)
        return progress if isinstance(progress, int) else 0

    def _identity_playable(self, color, num, board, played):
        progress = self._progress_for_color(color, board, played)
        return isinstance(num, int) and num == progress + 1

    def _identity_safe(self, color, num, board, played):
        progress = self._progress_for_color(color, board, played)
        return isinstance(num, int) and num <= progress

    def _entry_playability_metrics(self, entry, board, played):
        identities = self._all_identities(entry)
        if not identities:
            return False, False, 0.0, 0

        playable = [(c, n) for (c, n) in identities if self._identity_playable(c, n, board, played)]
        certain = len(playable) == len(identities) and len(playable) > 0
        potential = len(playable) > 0
        play_prob = float(len(playable)) / float(len(identities))
        best_rank = max((n for _, n in playable), default=0)
        return certain, potential, play_prob, best_rank

    def _entry_safe_to_discard(self, entry, board, played):
        identities = self._all_identities(entry)
        if not identities:
            return False
        return all(self._identity_safe(c, n, board, played) for c, n in identities)

    def _visible_identity_counts(self, hands, trash, played):
        counts = {}
        for i, hand in enumerate(hands or []):
            if i == self.pnr:
                continue
            for card in self._as_cards(hand):
                c, n = self._card_color_num(card)
                if c is None or n is None:
                    continue
                counts[(c, n)] = counts.get((c, n), 0) + 1

        for container in (trash, played):
            for card in self._as_cards(container):
                c, n = self._card_color_num(card)
                if c is None or n is None:
                    continue
                counts[(c, n)] = counts.get((c, n), 0) + 1

        return counts

    def _remaining_copies(self, hands, trash, played, color, num):
        total = self._identity_total_copies(num)
        counts = self._visible_identity_counts(hands, trash, played)
        seen = counts.get((color, num), 0)
        return max(total - seen, 0)

    def _match_action(self, valid_actions, action_type, **kwargs):
        for action in valid_actions or []:
            if getattr(action, "type", None) != action_type:
                continue
            ok = True
            for key, value in kwargs.items():
                if getattr(action, key, None) != value:
                    ok = False
                    break
            if ok:
                return action
        return None

    def _hint_matches_entry(self, entry, hint):
        colors, nums, touched = self._entry_info(entry)

        if touched is False:
            return False
        if touched is True:
            return True

        if hint.type == HINT_COLOR:
            if colors is None:
                exact_color, _ = self._card_color_num(entry)
                return exact_color == hint.col
            return hint.col in colors

        if hint.type == HINT_NUMBER:
            if nums is None:
                _, exact_num = self._card_color_num(entry)
                return exact_num == hint.num
            return hint.num in nums

        return False

    def _resolve_fresh_hint(self, hint, my_state, board, played, valid_actions):
        cards = self._as_cards(my_state)
        if not cards:
            return None

        touched = [idx for idx, entry in enumerate(cards) if self._hint_matches_entry(entry, hint)]
        if not touched:
            return None

        certain = []
        potential = []
        for idx in touched:
            entry = cards[idx]
            playable, maybe, _, _ = self._entry_playability_metrics(entry, board, played)
            if playable:
                certain.append(idx)
            elif maybe:
                potential.append(idx)

        if certain:
            idx = max(certain)
            return self._match_action(valid_actions, PLAY, cnr=idx)
        if potential:
            idx = max(potential)
            return self._match_action(valid_actions, PLAY, cnr=idx)
        return None

    def _select_own_play(self, my_state, board, played, valid_actions):
        cards = self._as_cards(my_state)
        if not cards:
            return None

        playable_indices = []
        for idx, entry in enumerate(cards):
            certain, _, _, _ = self._entry_playability_metrics(entry, board, played)
            if certain:
                playable_indices.append(idx)

        if not playable_indices:
            return None

        idx = max(playable_indices)
        return self._match_action(valid_actions, PLAY, cnr=idx)

    def _select_hint(self, hands, nr, board, played, valid_actions):
        best = []
        best_score = None

        for target, hand_state in enumerate(hands or []):
            if target == nr:
                continue

            hand = self._as_cards(hand_state)
            if not hand:
                continue

            colors = []
            nums = []
            for card in hand:
                c, n = self._card_color_num(card)
                if c is not None and c not in colors:
                    colors.append(c)
                if n is not None and n not in nums:
                    nums.append(n)

            for col in colors:
                action = self._match_action(valid_actions, HINT_COLOR, pnr=target, col=col)
                if action is None:
                    continue
                touched = [i for i, card in enumerate(hand) if self._card_color_num(card)[0] == col]
                playable = [i for i in touched if self._identity_playable(self._card_color_num(hand[i])[0], self._card_color_num(hand[i])[1], board, played)]
                if not playable:
                    continue
                best_rank = max((self._card_color_num(hand[i])[1] for i in playable), default=0)
                nonplayable = len(touched) - len(playable)
                score = (best_rank, -len(touched), -nonplayable, max(playable))
                if best_score is None or score > best_score:
                    best_score = score
                    best = [action]
                elif score == best_score:
                    best.append(action)

            for num in nums:
                action = self._match_action(valid_actions, HINT_NUMBER, pnr=target, num=num)
                if action is None:
                    continue
                touched = [i for i, card in enumerate(hand) if self._card_color_num(card)[1] == num]
                playable = [i for i in touched if self._identity_playable(self._card_color_num(hand[i])[0], self._card_color_num(hand[i])[1], board, played)]
                if not playable:
                    continue
                best_rank = num
                nonplayable = len(touched) - len(playable)
                score = (best_rank, -len(touched), -nonplayable, max(playable))
                if best_score is None or score > best_score:
                    best_score = score
                    best = [action]
                elif score == best_score:
                    best.append(action)

        if best:
            return random.choice(best)
        return None

    def _select_safe_discard(self, my_state, board, played, valid_actions):
        cards = self._as_cards(my_state)
        if not cards:
            return None

        safe_indices = [idx for idx, entry in enumerate(cards) if self._entry_safe_to_discard(entry, board, played)]
        if not safe_indices:
            return None

        idx = min(safe_indices)
        return self._match_action(valid_actions, DISCARD, cnr=idx)

    def _risk_score(self, entry, hands, trash, played, board):
        identities = self._all_identities(entry)
        if not identities:
            return float("inf")

        certainty_count = float(len(identities))
        play_prob = 0.0
        avg_rank = 0.0
        avg_criticality = 0.0

        for color, num in identities:
            if self._identity_playable(color, num, board, played):
                play_prob += 1.0
            avg_rank += float(num)
            remaining = self._remaining_copies(hands, trash, played, color, num)
            avg_criticality += 1.0 / float(max(remaining, 1))

        play_prob /= certainty_count
        avg_rank /= certainty_count
        avg_criticality /= certainty_count

        maybe_five = 1.0 if any(num == 5 for _, num in identities) else 0.0
        maybe_four = 1.0 if any(num == 4 for _, num in identities) else 0.0

        return (play_prob * 120.0) + (avg_rank * 4.0) + (avg_criticality * 40.0) + (maybe_five * 25.0) + (maybe_four * 8.0)

    def _select_risky_discard(self, my_state, hands, trash, played, board, valid_actions):
        cards = self._as_cards(my_state)
        if not cards:
            return None

        best = []
        best_score = None
        for idx, entry in enumerate(cards):
            action = self._match_action(valid_actions, DISCARD, cnr=idx)
            if action is None:
                continue
            score = self._risk_score(entry, hands, trash, played, board)
            if best_score is None or score < best_score:
                best_score = score
                best = [action]
            elif score == best_score:
                best.append(action)

        if best:
            return random.choice(best)
        return None
