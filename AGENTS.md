# AGENTS.md

## Repository purpose
`pyhanabi` is a Python Hanabi engine plus a minimal browser UI used for AI experiments and human+AI gameplay.

## Key architecture points
- `hanabi.py` is the core: game rules, cards/actions, AI classes, and CLI simulation entrypoint.
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
