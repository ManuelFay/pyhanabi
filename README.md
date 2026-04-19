# pyhanabi

`pyhanabi` is a Hanabi research repository focused on **recursive self-improvement loops for AI agents**:
- self-play and cross-play experiments,
- recursive/partner-modeling strategies,
- LLM-in-the-loop decision policies,
- reproducible logs for post-run analysis.

The project supports both:
- **CLI experiments** for high-throughput AI runs, and
- a lightweight **HTTP UI** for interactive human+AI games and replay inspection.

## Natural-language strategy synthesis (new)

Humans can now author strategy principles in markdown, then generate executable strategy code with an LLM:

1. Write a design doc in `human_strategies/*.md`.
2. Generate a strategy module with `scripts/generate_strategy_from_principles.py`.
3. Register the strategy alias in `strategies/__init__.py`.
4. Evaluate self-play performance in a leaderboard with:
   - mean score over 200 runs,
   - perfect-game count (`score == 25`).

Bootstrap included in this repository:
- design doc: `human_strategies/prior_strategy_principles.md`,
- generated code: `strategies/human_prior_principles_strategy.py`,
- alias: `human-prior`.

Second minimal example included:
- design doc: `human_strategies/single_immediate_hint_strategy_principles.md`,
- generated code: `strategies/human_single_hint_strategy.py`,
- alias: `human-single-hint`.

---

## Research framing

This repository is organized around iterative agent improvement:
1. run experiments (self-play, mirrored play, ablations),
2. inspect outcomes and reasoning traces,
3. refine strategy logic or prompts,
4. run again.

### Strategy families

- **Heuristic strategies** (deterministic/procedural): operate on explicit game-state rules and hand-crafted conventions.
- **LLM strategies** (`llm`, `fast-llm`, `feedback-llm`): include a language model directly in the action-selection reasoning loop.

In broad project history terms:
- the original strategy set was human-authored,
- more recent additions (including `prior` and the LLM variants) are AI-designed / AI-assisted research artifacts.

---

## Repository structure (current)

- `hanabi.py`  
  Core engine + CLI simulation entrypoint (rules, turns, actions, game loop).

- `strategies/`  
  Strategy package (one strategy per file).
  - `strategies/base.py`: `AbstractStrategy` contract + shared helpers.
  - `strategies/__init__.py`: strategy registry (`STRATEGY_TYPES`) used by CLI/runtime lookups.

- `httpui.py`  
  Minimal stdlib HTTP server for interactive gameplay, replays, and survey-backed study flows.

- `docs/llm_hanabi_context.md`  
  Main context pack/prompt reference used by LLM strategy implementations.

- `scripts/ai_vs_ai_average.py`  
  Batch experiment runner for same-strategy AI-vs-AI averages.

- `scripts/generate_strategy_from_principles.py`  
  LLM-driven code generator from human principles markdown.

- `scripts/human_strategy_leaderboard.py`  
  Self-play evaluator that writes a markdown leaderboard with mean score + perfect games.

- `human_strategies/`  
  Human-authored strategy principles and manifest for generated strategy mappings.

- `log/`  
  Runtime outputs:
  - `log/game*.log` game traces,
  - `log/survey*.log` survey/study traces,
  - `log/llm_api_calls.jsonl` raw LLM request/response traces,
  - `log/llm_play_logs/` per-game human-readable LLM reasoning logs.

---

## Setup

```bash
./scripts/setup_env.sh
source .venv/bin/activate
```

Python 3.10+ is expected.

---

## CLI: run experiments

## 1) Direct engine CLI

```bash
python hanabi.py random random --games 50
python hanabi.py prior prior --games 50
python hanabi.py llm random --games 5
```

Notes:
- Positional args are strategy names for player 0 and player 1.
- `--games N` controls repeated runs.
- Use `--show-reasoning` with LLM strategies when you want turn-by-turn reasoning output in stdout.

List available strategy aliases:

```bash
python - <<'PY'
import hanabi
print(sorted(hanabi.get_playertypes().keys()))
PY
```

## 2) Batch experiment helper

```bash
python scripts/ai_vs_ai_average.py --games 100
python scripts/ai_vs_ai_average.py --strategies prior llm feedback-llm --games 20 --show-reasoning
```

This script runs same-strategy AI-vs-AI experiments and prints aggregate summaries.

## 3) Human-principles leaderboard run (200-game scorecard)

```bash
python scripts/human_strategy_leaderboard.py --games 200
```

The output markdown leaderboard is written to `docs/human_strategy_leaderboard.md`.

---

## Interactive play via HTTP UI

Start server:

```bash
python httpui.py
```

Then open:

- `http://127.0.0.1:31337/` for normal interactive launch,
- `http://127.0.0.1:31337/selectai/` to pick a specific AI opponent,
- `http://127.0.0.1:31337/selectreplay/` to browse replay logs.

The HTTP UI is intentionally dependency-light (stdlib server, HTML rendered directly).

---

## Running LLM-in-the-loop agents

Set environment variables before launching LLM strategies:

```bash
export OPENAI_API_KEY="sk-..."
# Optional tuning:
export PYHANABI_OPENAI_MODEL="gpt-5.4-mini"
export PYHANABI_OPENAI_REASONING_EFFORT="low"
```

Useful log controls:

```bash
export PYHANABI_LLM_LOG_PATH="log/llm_api_calls.jsonl"
export PYHANABI_LLM_PLAY_LOG_DIR="log/llm_play_logs"
```

Generate a strategy from a human principles markdown:

```bash
python scripts/generate_strategy_from_principles.py \
  human_strategies/prior_strategy_principles.md \
  strategies/human_prior_principles_strategy.py \
  --class-name HumanPriorPrinciplesStrategy
```

The generator prompt explicitly constrains the model to use only the provided principles doc and the engine/base strategy contract.

---

## Where to point an AI agent for iterative improvement

If you are running an autonomous/assistant-style improvement loop, start the agent with these anchor files:

1. `strategies/` (implementation targets),
2. `strategies/__init__.py` (registration/CLI aliases),
3. `hanabi.py` (runtime + simulation loop contract),
4. `human_strategies/` (human design docs to convert into executable strategies),
5. `docs/llm_hanabi_context.md` (LLM behavior/context source of truth),
6. `log/` outputs + `docs/human_strategy_leaderboard.md` (empirical feedback for refinement).

Typical loop:
- edit/add principles markdown in `human_strategies/`,
- generate/update strategy code with `scripts/generate_strategy_from_principles.py`,
- run `python scripts/human_strategy_leaderboard.py --games 200`,
- inspect `docs/human_strategy_leaderboard.md`, `log/llm_play_logs/`, and `log/game*.log`,
- iterate.

---

## Quick maintenance checks

```bash
python -m py_compile hanabi.py httpui.py tutorial.py consent.py serverconf.py
python hanabi.py random random --games 5
```

For adding new strategies, see `docs/adding_strategy.md`.
