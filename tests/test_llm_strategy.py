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


class _FakeResponse:
    def __init__(self, text):
        self.output_text = text


class _FakeResponsesApi:
    def __init__(self, text):
        self._text = text

    def create(self, **kwargs):
        return _FakeResponse(self._text)


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
    assert "selected_action_id" in entry["response_text"]
    assert entry["error"] is None
