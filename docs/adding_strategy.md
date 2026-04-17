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
