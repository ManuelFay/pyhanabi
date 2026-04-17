# Adding a New Strategy

Strategies now live in the dedicated `strategies/` package with **one strategy per file**.

## Required pieces

1. Create a new file in `strategies/`, e.g. `strategies/my_strategy.py`.
2. In that file, define a strategy class that inherits from `AbstractStrategy`.
3. Implement `get_action(...)` at minimum. Optionally implement `inform(...)` and `get_explanation(...)`.
4. Register the class in `strategies/__init__.py` by adding it to `STRATEGY_TYPES`.

## Minimal custom strategy example

```python
# strategies/my_strategy.py
from strategies.base import AbstractStrategy
import random

class MyStrategy(AbstractStrategy):
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints):
        return random.choice(valid_actions)
```

Then update `strategies/__init__.py`:

```python
from .my_strategy import MyStrategy

STRATEGY_TYPES["my"] = MyStrategy
```

You can run it with:

```bash
python hanabi.py my my --games 100
```


## LLM strategy notes

A starter LLM-backed strategy is available as `llm` and lives in `strategies/llm_strategy.py`.

```bash
python hanabi.py llm random --games 5
```

Runtime configuration:
- `OPENAI_API_KEY` (required to call API)
- `PYHANABI_OPENAI_MODEL` (optional, default `gpt-5.4-mini`)
- `PYHANABI_OPENAI_REASONING_EFFORT` (optional, default `low`)
- `PYHANABI_LLM_LOG_PATH` (optional, default `log/llm_api_calls.jsonl`)
- `PYHANABI_LLM_PLAY_LOG_DIR` (optional, default `log/llm_play_logs/`)

Where to put your API key:
- In your shell session before running: `export OPENAI_API_KEY="sk-..."`
- Or in your shell profile (e.g. `~/.bashrc`) so it is available in new terminals.

The implementation enforces legality by requiring the model to output a `selected_action_id` that indexes directly into the supplied `legal_actions` list, then validating every returned action field before constructing the engine `Action` object. If the model does not return a legal action, the strategy now raises a clear error message instead of silently falling back.
Each request/response exchange is logged to JSONL so you can inspect exact payloads and model outputs.
Additionally, each LLM player writes a per-game human-readable play log under `log/llm_play_logs/` that includes board state, points, mistakes, hints, visible opponent cards, opponent knowledge, own knowledge, reasoning text, and chosen action.
At game end, the strategy requests a `gpt-5.4` medium-reasoning postgame review and appends the analysis to the same file.


Prompt source of truth:
- `docs/llm_hanabi_context.md` is injected into every LLM turn as the context pack.
- Future prompt optimizations should usually start by updating this context file and tests.

To inspect reasoning in AI-vs-AI CLI runs:

```bash
python hanabi.py llm llm --games 1 --show-reasoning
python scripts/ai_vs_ai_average.py --strategies llm --games 3 --show-reasoning
```

With `--show-reasoning`, CLI logs now include parseable per-move state lines:
`STATE move=<n> player=<idx> points=<score> hints=<h> mistakes=<m> board=[green:x, ...]`
