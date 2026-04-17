# AGENTS.md

## Repository purpose
`pyhanabi` is a Python Hanabi engine plus a minimal browser UI used for AI experiments and human+AI gameplay.

## Key architecture points
- `hanabi.py` is the core runtime: game rules, cards/actions, game loop, and CLI simulation entrypoint.
- Strategies are now organized under `strategies/` (one strategy per file).
  - `strategies/base.py` defines the abstract strategy contract (`AbstractStrategy`) plus shared helper utilities used across strategies.
  - `strategies/__init__.py` is the registry (`STRATEGY_TYPES`) consumed by `hanabi.py`.
  - Concrete strategy files now contain full strategy logic (no legacy-adapter delegation).
- `httpui.py` is a lightweight HTTP server (no framework) that renders HTML directly and routes game actions.
- `tutorial.py` and `consent.py` store static HTML strings used by study/tutorial flows.
- `serverconf.py` controls default bind host/port.

## Practical maintenance notes
- Treat this as a Python 3-only codebase.
- `BaseHTTPRequestHandler` writes bytes: use `MyHandler._write(...)` for text responses.
- Keep webserver behavior dependency-light (stdlib-first approach).
- Prefer deterministic quick checks when possible:
  - `python -m py_compile ...`
  - `python hanabi.py random random --games 5`

## Common run commands
- Web UI: `python httpui.py` then open `http://127.0.0.1:31337/`
- CLI sims: `python hanabi.py random outer --games 100`

## Logging/data
- Runtime logs are written under `log/`.
- Replay and survey flows expect those log files to exist and be readable.

## Strategy maintenance workflow
- Add/update strategies in `strategies/` first; keep one strategy class per file.
- Register every strategy in `strategies/__init__.py` so CLI aliases work (`python hanabi.py <a> <b>`).
- Prefer inheriting from `AbstractStrategy` for all new strategy implementations.
- See `docs/adding_strategy.md` for authoring and registration details.

## Suggested next refactors
- Add typed interfaces/protocols for strategy input/output state to reduce coupling.
- Split `hanabi.py` into focused modules (deck/rules/actions/game loop/CLI).
- Add lightweight tests for strategy registry loading and one-game smoke runs per strategy.
- Introduce a strategy factory module and optional config-driven experiment runner.
