import io
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hanabi


class _ReasoningPlayer:
    def __init__(self, name, pnr):
        self.name = name
        self._explanation = ["because test"]

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        return valid_actions[0]

    def inform(self, action, player, game):
        pass

    def get_explanation(self):
        return self._explanation


def test_game_show_reasoning_prints_explanations():
    log = io.StringIO()
    players = [_ReasoningPlayer("A", 0), _ReasoningPlayer("B", 1)]
    game = hanabi.Game(players, log=log, show_reasoning=True)
    game.run(turns=2)
    output = log.getvalue()
    assert "reasoning:" in output
    assert "because test" in output
    assert "STATE move=" in output
    assert "points=" in output
    assert "hints=" in output
    assert "mistakes=" in output
