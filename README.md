# pyhanabi

A research-oriented Hanabi implementation with:
- a **CLI simulator** for AI-vs-AI runs,
- a lightweight **web UI server** for human+AI play,
- several baseline and intentional AI agents.

## Quick start

### 1) Rapid install (recommended)

```bash
./scripts/setup_env.sh
```

This creates `.venv`, upgrades packaging tools, and installs runtime/test dependencies.

### 2) Activate environment

```bash
source .venv/bin/activate
```

### 3) Run the web UI

```bash
python httpui.py
# then open http://127.0.0.1:31337/
```

### 4) Run CLI simulations

```bash
python hanabi.py random random --games 50
```

---

## Installation details

### Requirements
- Python 3.10+ (tested on Python 3.12)

### Manual setup (alternative)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

---

## Package tour

### Core engine
- `hanabi.py`
  - game rules, card/deck utilities, action model,
  - game loop/simulation entry point and strategy loading,
  - CLI entry point for repeated simulation runs.

- `strategies/`
  - one strategy per Python file,
  - shared abstract strategy contract in `strategies/base.py`,
  - strategy registry in `strategies/__init__.py`.

### Web server / UI
- `httpui.py`
  - HTTP server and routing,
  - renders game state and handles actions,
  - supports normal games, replay flows, and survey paths.

### Content/config modules
- `tutorial.py` — HTML strings for the in-app tutorial/rules.
- `consent.py` — consent form HTML used in study mode.
- `serverconf.py` — host/port config (`127.0.0.1:31337` by default).

### Supporting files
- `scripts/setup_env.sh` — one-command environment bootstrap.
- `requirements.txt` — runtime + test dependencies.
- `CHANGELOG.md` — summary of modernization work.
- `AGENTS.md` — maintainer notes for contributors/agents.

---

## Typical workflows

### Play in browser
1. Start server with `python httpui.py`.
2. Open `http://127.0.0.1:31337/`.
3. Pick an AI from the landing page.

### Run AI benchmarks quickly

```bash
python hanabi.py random outer --games 200
python hanabi.py intentional full --games 200
```

### Developer checks

```bash
python -m py_compile hanabi.py httpui.py tutorial.py consent.py serverconf.py
python hanabi.py random random --games 5
```

### Add a strategy
See `docs/adding_strategy.md` for the step-by-step workflow and registry changes.

---

## Notes on Python modernization

This codebase was upgraded to run on current Python 3 versions. Highlights include:
- migration from Python 2 syntax/APIs,
- HTTP response encoding fixes for `http.server`,
- replacement of old `file(...)` usage with `open(...)`,
- CLI stats fallback to stdlib `statistics` (no hard `numpy` requirement),
- streamlined form parsing for URL-encoded form submissions.

See `CHANGELOG.md` for details.
