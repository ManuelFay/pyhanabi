"""Feedback-oriented LLM strategy with deterministic risk labels."""

import json
from pathlib import Path

from hanabi import COLORNAMES, HINT_COLOR, HINT_NUMBER, PLAY, DISCARD
from .llm_strategy import LLMStrategy


class FeedbackLLMStrategy(LLMStrategy):
    """LLM strategy variant that injects strict policy and rule-checker labels."""

    POLICY_PATH = Path(__file__).resolve().parents[1] / "docs" / "feedback_llm_policy.md"

    SYSTEM_PROMPT = (
        "You are a Hanabi planner following strict safety policy. Choose one legal action only. "
        "Always separate possible from certain. Return strict JSON only."
    )

    def _load_context_markdown(self):
        base = super()._load_context_markdown()
        policy = self.POLICY_PATH.read_text(encoding="utf-8")
        return base + "\n\n" + policy

    def _card_possibilities(self, card_knowledge):
        result = []
        for col in range(len(card_knowledge)):
            for rank_idx, count in enumerate(card_knowledge[col]):
                if count > 0:
                    result.append((col, rank_idx + 1))
        return result

    def _classify_card(self, possibilities, board):
        if not possibilities:
            return {
                "certain_play": False,
                "possible_play": False,
                "safe_discard": False,
                "dangerous_discard": True,
                "critical": True,
            }
        playable_flags = [(board[col][1] + 1 == rank) for (col, rank) in possibilities]
        discardable_flags = [(board[col][1] >= rank) for (col, rank) in possibilities]
        critical = any(rank == 5 for (_, rank) in possibilities)
        return {
            "certain_play": all(playable_flags),
            "possible_play": any(playable_flags),
            "safe_discard": all(discardable_flags) and not critical,
            "dangerous_discard": (not all(discardable_flags)) or critical,
            "critical": critical,
        }

    def _action_touched_cards(self, action, hands, nr):
        if action["type"] == "hint_color":
            pnr = action["pnr"]
            if pnr is None or pnr >= len(hands):
                return []
            return [i for i, (col, _) in enumerate(hands[pnr]) if col == action["col"]]
        if action["type"] == "hint_number":
            pnr = action["pnr"]
            if pnr is None or pnr >= len(hands):
                return []
            return [i for i, (_, rank) in enumerate(hands[pnr]) if rank == action["num"]]
        if action["type"] in ["play", "discard"]:
            return [action["cnr"]]
        return []

    def _serialize_state(self, nr, hands, knowledge, trash, played, board, hints, legal_actions):
        board_state = {COLORNAMES[col]: rank for (col, rank) in board}
        next_playable = {COLORNAMES[col]: rank + 1 for (col, rank) in board}

        own_cards = []
        for card_idx, card_knowledge in enumerate(knowledge[nr]):
            possibilities = self._card_possibilities(card_knowledge)
            labels = self._classify_card(possibilities, board)
            own_cards.append(
                {
                    "card_index": card_idx,
                    "possible_identities": [
                        {"color": COLORNAMES[col], "rank": rank} for (col, rank) in possibilities[:12]
                    ],
                    "labels": labels,
                }
            )

        opponent_views = []
        for pnr, hand in enumerate(hands):
            if pnr == nr:
                continue
            opponent_views.append(
                {
                    "player": pnr,
                    "cards": [
                        {"card_index": idx, "color": COLORNAMES[col], "rank": rank}
                        for idx, (col, rank) in enumerate(hand)
                    ],
                    "opponent_knowledge": [
                        self._card_possibilities(card_knowledge)[:10] for card_knowledge in knowledge[pnr]
                    ],
                }
            )

        enriched_actions = []
        for action in legal_actions:
            touched = self._action_touched_cards(action, hands, nr)
            enriched = dict(action)
            enriched["touched_cards"] = touched
            if action["type"] in ["play", "discard"]:
                idx = action["cnr"]
                if idx is not None and idx < len(own_cards):
                    enriched["card_labels"] = own_cards[idx]["labels"]
            enriched_actions.append(enriched)

        return {
            "current_player": nr,
            "hints": hints,
            "board": board_state,
            "next_needed": next_playable,
            "own_cards": own_cards,
            "opponents": opponent_views,
            "recent_discarded_cards": trash[-10:],
            "recent_played_cards": played[-10:],
            "legal_actions": enriched_actions,
        }

    def _build_user_prompt(self, state_payload):
        protocol = {
            "protocol_name": "feedback-llm-v1",
            "required_output": {
                "selected_action_id": "int",
                "selected_action": {
                    "type": "str",
                    "pnr": "int|null",
                    "col": "int|null",
                    "num": "int|null",
                    "cnr": "int|null",
                    "canonical": "str",
                },
                "reasoning": "str",
                "strategy_feedback": {
                    "move": "str",
                    "intent": "PLAY|SAVE|DISCARD|SETUP|SAFE_DISCARD|RISK_PLAY",
                    "target_cards": "list[int]",
                    "why_not_play": "str",
                    "why_not_discard": "str",
                    "risk_level": "none|low|medium|high",
                    "is_redundant_clue": "bool",
                    "is_card_certain_playable": "bool",
                    "is_card_certain_discardable": "bool",
                },
            },
            "rules": [
                "Return exactly one legal action from legal_actions.",
                "selected_action_id must reference legal_actions[action_id].",
                "selected_action must exactly match that legal action.",
                "Output strict JSON only.",
            ],
        }
        return json.dumps(
            {
                "context_pack_markdown": self._load_context_markdown(),
                "protocol": protocol,
                "state": state_payload,
            },
            separators=(",", ":"),
        )

    def _llm_pick_action(self, state_payload, legal_actions):
        action, reason = super()._llm_pick_action(state_payload, legal_actions)
        return action, reason
