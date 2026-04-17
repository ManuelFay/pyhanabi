import os
import json

import pytest

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hanabi import Action, PLAY, DISCARD
from strategies.llm_strategy import LLMStrategy
from strategies.fast_llm_strategy import FastLLMStrategy


class _FakeResponse:
    def __init__(self, text):
        self.output_text = text


class _FakeResponsesApi:
    def __init__(self, text):
        self._texts = [text]

    def queue(self, text):
        self._texts.append(text)

    def create(self, **kwargs):
        if not self._texts:
            raise RuntimeError("No queued fake responses")
        return _FakeResponse(self._texts.pop(0))


class _FakeClient:
    def __init__(self, text):
        self.responses = _FakeResponsesApi(text)


def _make_strategy(payload_text):
    os.environ["OPENAI_API_KEY"] = "test-key"
    return LLMStrategy("LLM", 0, client=_FakeClient(payload_text))


def test_llm_strategy_returns_selected_legal_action():
    strategy = _make_strategy(
        '{"selected_action_id":1,"selected_action":{"type":"discard","pnr":null,"col":null,'
        '"num":null,"cnr":0,"canonical":"discard(card_index=0)"},"reasoning":"safe discard"}'
    )
    valid_actions = [Action(PLAY, cnr=0), Action(DISCARD, cnr=0)]

    action = strategy.get_action(
        nr=0,
        hands=[[], []],
        knowledge=[[[]], [[]]],
        trash=[],
        played=[],
        board=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
        valid_actions=valid_actions,
        hints=8,
    )

    assert action == Action(DISCARD, cnr=0)


def test_llm_strategy_raises_on_illegal_action_id():
    strategy = _make_strategy(
        '{"selected_action_id":9,"selected_action":{"type":"discard","pnr":null,"col":null,'
        '"num":null,"cnr":0,"canonical":"discard(card_index=0)"},"reasoning":"oops"}'
    )
    valid_actions = [Action(PLAY, cnr=0), Action(DISCARD, cnr=0)]

    with pytest.raises(ValueError, match="not a legal action"):
        strategy.get_action(
            nr=0,
            hands=[[], []],
            knowledge=[[[]], [[]]],
            trash=[],
            played=[],
            board=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
            valid_actions=valid_actions,
            hints=8,
        )


def test_llm_strategy_includes_context_pack_in_prompt(tmp_path):
    payload = '{"selected_action_id":0,"selected_action":{"type":"play","pnr":null,"col":null,"num":null,"cnr":0,"canonical":"play(card_index=0)"},"reasoning":"play"}'
    strategy = _make_strategy(payload)
    context_file = tmp_path / "llm_hanabi_context.md"
    context_file.write_text("# TEST CONTEXT", encoding="utf-8")
    strategy.CONTEXT_PATH = context_file

    prompt = strategy._build_user_prompt({"legal_actions": []})
    assert "TEST CONTEXT" in prompt


def test_llm_state_dump_includes_adapted_summaries(tmp_path):
    payload = '{"selected_action_id":0,"selected_action":{"type":"play","pnr":null,"col":null,"num":null,"cnr":0,"canonical":"play(card_index=0)"},"reasoning":"play"}'
    strategy = _make_strategy(payload)
    context_file = tmp_path / "llm_hanabi_context.md"
    context_file.write_text("# TEST CONTEXT", encoding="utf-8")
    strategy.CONTEXT_PATH = context_file

    state = strategy._serialize_state(
        nr=0,
        hands=[[], [(0, 1), (4, 2)]],
        knowledge=[[[[1, 0, 0, 0, 0] for _ in range(5)]], [[[1, 0, 0, 0, 0] for _ in range(5)]]],
        trash=[],
        played=[],
        board=[(0, 1), (1, 0), (2, 0), (3, 2), (4, 0)],
        hints=7,
        legal_actions=[{"action_id": 0, "type": "play"}],
    )
    assert "board_summary" in state
    assert "visible_hands_summary" in state
    assert "own_knowledge_summary" in state
    assert state["board_summary"]["next_playable_rank_by_color"]["green"] == 2


def test_llm_strategy_logs_request_and_response(tmp_path):
    payload = (
        '{"selected_action_id":0,"selected_action":{"type":"play","pnr":null,"col":null,'
        '"num":null,"cnr":0,"canonical":"play(card_index=0)"},"reasoning":"go"}'
    )
    strategy = _make_strategy(payload)
    context_file = tmp_path / "llm_hanabi_context.md"
    context_file.write_text("# TEST CONTEXT", encoding="utf-8")
    strategy.CONTEXT_PATH = context_file
    strategy.log_path = tmp_path / "llm_calls.jsonl"

    valid_actions = [Action(PLAY, cnr=0)]
    action = strategy.get_action(
        nr=0,
        hands=[[], []],
        knowledge=[[[]], [[]]],
        trash=[],
        played=[],
        board=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
        valid_actions=valid_actions,
        hints=8,
    )
    assert action == Action(PLAY, cnr=0)
    assert strategy.log_path.exists()

    lines = strategy.log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["request"]["model"] == strategy.model
    assert entry["request"]["reasoning"]["effort"] == "low"
    assert "selected_action_id" in entry["response_text"]
    assert entry["error"] is None


def test_llm_strategy_writes_per_game_human_log_and_review(tmp_path):
    action_payload = (
        '{"selected_action_id":0,"selected_action":{"type":"play","pnr":null,"col":null,'
        '"num":null,"cnr":0,"canonical":"play(card_index=0)"},"reasoning":"safe play"}'
    )
    strategy = _make_strategy(action_payload)
    strategy.play_log_dir = tmp_path

    context_file = tmp_path / "llm_hanabi_context.md"
    context_file.write_text("# TEST CONTEXT", encoding="utf-8")
    strategy.CONTEXT_PATH = context_file

    class _DummyGame:
        hits = 3
        hints = 8
        board = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]

        def score(self):
            return 0

    strategy.start_game(_DummyGame())

    valid_actions = [Action(PLAY, cnr=0)]
    strategy.get_action(
        nr=0,
        hands=[[], [(0, 1)]],
        knowledge=[[[[1, 0, 0, 0, 0] for _ in range(5)]], [[[1, 0, 0, 0, 0] for _ in range(5)]]],
        trash=[],
        played=[],
        board=[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
        valid_actions=valid_actions,
        hints=8,
    )
    strategy.client.responses.queue("Overall, main issue was over-hinting in early game.")
    strategy.on_game_end(_DummyGame())

    assert strategy._current_game_file.exists()
    content = strategy._current_game_file.read_text(encoding="utf-8")
    assert "opponent_cards:" in content
    assert "llm_own_knowledge:" in content
    assert "llm_reasoning: safe play" in content
    assert "llm_action: play(card_index=0)" in content
    assert "POSTGAME_REVIEW" in content


def test_fast_llm_strategy_uses_compact_state():
    strategy = FastLLMStrategy(
        "Fast",
        0,
        client=_FakeClient(
            '{"selected_action_id":0,"selected_action":{"type":"play","pnr":null,"col":null,"num":null,"cnr":0,"canonical":"play(card_index=0)"},"reasoning":"x"}'
        ),
    )
    state = strategy._serialize_state(
        nr=0,
        hands=[[], [(0, 1), (3, 2)]],
        knowledge=[[[[1, 0, 0, 0, 0] for _ in range(5)]], [[[1, 0, 0, 0, 0] for _ in range(5)]]],
        trash=[(1, 3)],
        played=[(0, 1)],
        board=[(0, 1), (1, 0), (2, 0), (3, 0), (4, 0)],
        hints=6,
        legal_actions=[{"action_id": 0, "type": "play", "pnr": None, "col": None, "num": None, "cnr": 0, "canonical": "play(card_index=0)"}],
    )
    assert "knowledge" not in state
    assert "board" in state
    assert "own_knowledge_summary" in state
    assert "recent_discarded_cards" in state
