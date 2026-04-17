"""LLM-backed strategy implementation with strict legal-action protocol."""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

from .base import AbstractStrategy
from hanabi import Action, HINT_COLOR, HINT_NUMBER, PLAY, DISCARD, COLORNAMES

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional runtime dependency
    OpenAI = None


class LLMStrategy(AbstractStrategy):
    """Use an LLM to choose among legal actions with strict validation."""

    CONTEXT_PATH = Path(__file__).resolve().parents[1] / "docs" / "llm_hanabi_context.md"
    DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "log" / "llm_api_calls.jsonl"

    SYSTEM_PROMPT = (
        "You are an expert Hanabi partner. Read the context pack carefully and then choose "
        "exactly one legal action. You must return strict JSON only with the required schema."
    )

    def __init__(self, name, pnr, client=None):
        self.name = name
        self.pnr = pnr
        self.explanation = []
        self.model = os.getenv("PYHANABI_OPENAI_MODEL", "gpt-5.4-mini")
        self.reasoning_effort = os.getenv("PYHANABI_OPENAI_REASONING_EFFORT", "low")
        self.log_path = Path(os.getenv("PYHANABI_LLM_LOG_PATH", str(self.DEFAULT_LOG_PATH)))
        if client is not None:
            self.client = client
        elif OpenAI and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None

    def _action_type_name(self, action_type):
        mapping = {
            HINT_COLOR: "hint_color",
            HINT_NUMBER: "hint_number",
            PLAY: "play",
            DISCARD: "discard",
        }
        return mapping[action_type]

    def _canonical_action(self, action):
        if action.type == HINT_COLOR:
            return f"hint_color(player={action.pnr}, color={COLORNAMES[action.col]})"
        if action.type == HINT_NUMBER:
            return f"hint_number(player={action.pnr}, number={action.num})"
        if action.type == PLAY:
            return f"play(card_index={action.cnr})"
        return f"discard(card_index={action.cnr})"

    def _serialize_action(self, action_id, action):
        return {
            "action_id": action_id,
            "type": self._action_type_name(action.type),
            "pnr": action.pnr,
            "col": action.col,
            "num": action.num,
            "cnr": action.cnr,
            "canonical": self._canonical_action(action),
        }

    def _serialize_state(self, nr, hands, knowledge, trash, played, board, hints, legal_actions):
        def summarize_visible_hands():
            result = []
            for pnr, hand in enumerate(hands):
                if pnr == nr:
                    result.append({"player": pnr, "cards": "hidden_to_current_player"})
                    continue
                cards = []
                for card_idx, (col, rank) in enumerate(hand):
                    cards.append(
                        {
                            "card_index": card_idx,
                            "color_index": col,
                            "color_name": COLORNAMES[col],
                            "rank": rank,
                        }
                    )
                result.append({"player": pnr, "cards": cards})
            return result

        def summarize_own_knowledge():
            result = []
            for card_idx, card_knowledge in enumerate(knowledge[nr]):
                candidates = []
                total = sum([sum(col_counts) for col_counts in card_knowledge]) or 1
                for col in range(len(card_knowledge)):
                    for rank_idx, count in enumerate(card_knowledge[col]):
                        if count > 0:
                            candidates.append(
                                {
                                    "color_index": col,
                                    "color_name": COLORNAMES[col],
                                    "rank": rank_idx + 1,
                                    "weight": count,
                                    "approx_probability": round(count / float(total), 4),
                                }
                            )
                candidates.sort(key=lambda x: (-x["weight"], x["color_index"], x["rank"]))
                result.append(
                    {
                        "card_index": card_idx,
                        "candidate_count": len(candidates),
                        "top_candidates": candidates[:8],
                    }
                )
            return result

        board_state = {
            COLORNAMES[col]: rank
            for (col, rank) in board
        }
        next_playable = {color_name: rank + 1 for color_name, rank in board_state.items()}
        safely_discardable_upto = {color_name: rank for color_name, rank in board_state.items()}
        return {
            "current_player": nr,
            "hints": hints,
            "board_summary": {
                "current_stacks": board_state,
                "next_playable_rank_by_color": next_playable,
                "safely_discardable_ranks_upto_by_color": safely_discardable_upto,
            },
            "visible_hands_summary": summarize_visible_hands(),
            "own_knowledge_summary": summarize_own_knowledge(),
            "visible_hands": hands,
            "knowledge": knowledge,
            "trash": trash,
            "played": played,
            "board": board_state,
            "legal_actions": legal_actions,
        }

    def _load_context_markdown(self):
        if not self.CONTEXT_PATH.exists():
            raise RuntimeError(f"Missing LLM context file: {self.CONTEXT_PATH}")
        return self.CONTEXT_PATH.read_text(encoding="utf-8")

    def _build_user_prompt(self, state_payload):
        protocol = {
            "protocol_name": "legal-action-id-v1",
            "rules": [
                "You must return one and only one legal action.",
                "selected_action_id must be exactly one action_id from legal_actions.",
                "selected_action must exactly match that legal action (type/pnr/col/num/cnr/canonical).",
                "If uncertain, still choose a legal action_id from the list.",
                "Output strict JSON only; no markdown fences and no extra keys.",
            ],
        }
        payload = {
            "context_pack_markdown": self._load_context_markdown(),
            "protocol": protocol,
            "state": state_payload,
        }
        return json.dumps(payload, separators=(",", ":"))

    def _log_exchange(self, request_payload, response_text, parsed_response=None, error_message=None):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "player_name": self.name,
            "player_index": self.pnr,
            "model": self.model,
            "request": request_payload,
            "response_text": response_text,
            "parsed_response": parsed_response,
            "error": error_message,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    def _extract_json(self, content):
        raw = content.strip()
        if raw.startswith("```"):
            lines = [line for line in raw.splitlines() if not line.strip().startswith("```")]
            raw = "\n".join(lines).strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in LLM response")
        return json.loads(raw[start:end + 1])

    def _to_action(self, candidate):
        action_type = {
            "hint_color": HINT_COLOR,
            "hint_number": HINT_NUMBER,
            "play": PLAY,
            "discard": DISCARD,
        }[candidate["type"]]
        return Action(
            action_type,
            pnr=candidate.get("pnr"),
            col=candidate.get("col"),
            num=candidate.get("num"),
            cnr=candidate.get("cnr"),
        )

    def _llm_pick_action(self, state_payload, legal_actions):
        if not self.client:
            raise RuntimeError(
                "LLMStrategy cannot call OpenAI: configure OPENAI_API_KEY and install openai package."
            )
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set.")

        request_payload = {
            "model": self.model,
            "reasoning": {"effort": self.reasoning_effort},
            "input": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": self._build_user_prompt(state_payload)},
            ],
        }
        response = self.client.responses.create(
            model=self.model,
            reasoning=request_payload["reasoning"],
            input=request_payload["input"],
        )
        response_text = response.output_text
        parsed = None
        try:
            parsed = self._extract_json(response_text)
        except Exception as exc:
            self._log_exchange(request_payload, response_text, parsed_response=None, error_message=str(exc))
            raise

        selected_id = parsed.get("selected_action_id")
        if not isinstance(selected_id, int):
            msg = "LLM protocol error: selected_action_id must be an integer legal action id."
            self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=msg)
            raise ValueError(msg)
        if selected_id < 0 or selected_id >= len(legal_actions):
            msg = f"LLM protocol error: selected_action_id={selected_id} is not a legal action."
            self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=msg)
            raise ValueError(msg)

        candidate = legal_actions[selected_id]
        selected_action = parsed.get("selected_action")
        if not isinstance(selected_action, dict):
            msg = "LLM protocol error: selected_action must be an object."
            self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=msg)
            raise ValueError(msg)

        required_keys = ["type", "pnr", "col", "num", "cnr", "canonical"]
        for key in required_keys:
            if key not in selected_action:
                msg = f"LLM protocol error: selected_action missing key: {key}"
                self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=msg)
                raise ValueError(msg)

        for key in required_keys:
            if selected_action[key] != candidate[key]:
                msg = (
                    "LLM protocol error: selected_action does not match legal action "
                    f"for key '{key}' (expected {candidate[key]!r}, got {selected_action[key]!r})."
                )
                self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=msg)
                raise ValueError(msg)

        reason = parsed.get("reasoning", "")
        self._log_exchange(request_payload, response_text, parsed_response=parsed, error_message=None)
        return self._to_action(candidate), reason

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        legal_actions = [self._serialize_action(i, action) for i, action in enumerate(valid_actions)]
        state_payload = self._serialize_state(
            nr=nr,
            hands=hands,
            knowledge=knowledge,
            trash=trash,
            played=played,
            board=board,
            hints=hints,
            legal_actions=legal_actions,
        )

        action, reasoning = self._llm_pick_action(state_payload, legal_actions)
        self.explanation = [f"LLM model={self.model}", reasoning]
        return action

    def inform(self, action, player, game):
        pass
