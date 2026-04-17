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
- `PYHANABI_OPENAI_MODEL` (optional, default `gpt-4.1-mini`)
- `PYHANABI_OPENAI_TEMPERATURE` (optional, default `0`)

Where to put your API key:
- In your shell session before running: `export OPENAI_API_KEY="sk-..."`
- Or in your shell profile (e.g. `~/.bashrc`) so it is available in new terminals.

The implementation enforces legality by requiring the model to output a `selected_action_id` that indexes directly into the supplied `legal_actions` list, then validating every returned action field before constructing the engine `Action` object. If the model does not return a legal action, the strategy now raises a clear error message instead of silently falling back.


Prompt source of truth:
- `docs/llm_hanabi_context.md` is injected into every LLM turn as the context pack.
- Future prompt optimizations should usually start by updating this context file and tests.
