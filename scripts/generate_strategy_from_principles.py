#!/usr/bin/env python3
"""Generate a Hanabi strategy module from a human-authored principles markdown file."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.4-mini"
ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate strategy Python code from a principles markdown file.")
    parser.add_argument("principles", help="Path to principles markdown file")
    parser.add_argument("output", help="Path to generated Python strategy module")
    parser.add_argument("--class-name", required=True, help="Class name to emit")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model (default: {DEFAULT_MODEL})")
    return parser.parse_args()


def extract_python(text: str) -> str:
    stripped = text.strip()
    if "```" not in stripped:
        return stripped
    parts = stripped.split("```")
    for block in parts:
        candidate = block.strip()
        if candidate.startswith("python"):
            return candidate[len("python"):].lstrip()
    return stripped


def _load_generation_context() -> str:
    """Load core engine/strategy contract context for robust code generation."""
    base_contract = (ROOT / "strategies/base.py").read_text(encoding="utf-8")
    hanabi_runtime = (ROOT / "hanabi.py").read_text(encoding="utf-8")

    contract_excerpt = []
    for line in base_contract.splitlines():
        if line.startswith("class AbstractStrategy") or line.strip().startswith("def __init__("):
            contract_excerpt.append(line)
        if line.strip().startswith("def get_action("):
            contract_excerpt.append(line)
            contract_excerpt.append('        """Return a legal action for the active player index `nr`."""')
            break

    action_lines = []
    capture = False
    for line in hanabi_runtime.splitlines():
        if line.strip().startswith("HINT_COLOR"):
            capture = True
        if capture:
            action_lines.append(line)
            if line.startswith("class Player(object):"):
                break

    valid_actions_lines = []
    capture = False
    for line in hanabi_runtime.splitlines():
        if line.strip().startswith("def valid_actions(self):"):
            capture = True
        if capture:
            valid_actions_lines.append(line)
            if line.strip().startswith("return valid"):
                break

    return (
        "Strategy base contract (excerpt):\n"
        + "\n".join(contract_excerpt)
        + "\n\nAction constants and Action fields (excerpt from hanabi.py):\n"
        + "\n".join(action_lines)
        + "\n\nGame.valid_actions implementation (excerpt):\n"
        + "\n".join(valid_actions_lines)
    )


def build_prompt(principles_path: Path, principles_text: str, class_name: str) -> str:
    context = _load_generation_context()
    return f"""
You are generating a new Hanabi strategy implementation.

Constraints:
- Use ONLY the principles in the provided markdown; do not reference or imitate any existing strategy names or modules.
- Output valid Python code only.
- Implement class `{class_name}` inheriting from `AbstractStrategy`.
- The class must expose: `__init__`, `get_action`, and optional `inform`.
- Imports allowed: `random`, `from .base import AbstractStrategy`, and symbols from `hanabi`.
- Ensure every returned action is legal from `valid_actions` or constructed from observed legal semantics.
- Include module docstring with source principles path: `{principles_path.as_posix()}`.

Core runtime context (authoritative excerpts):
---
{context}
---

Principles markdown:
---
{principles_text}
---
""".strip()


def generate_strategy_code(
    principles_path: Path,
    output_path: Path,
    class_name: str,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> str:
    """Generate strategy code from a principles markdown file and write it to disk."""
    principles_text = principles_path.read_text(encoding="utf-8")
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not resolved_api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate strategy code")

    prompt = build_prompt(principles_path, principles_text, class_name)
    client = OpenAI(api_key=resolved_api_key)
    response = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": "Return only Python code."},
            {"role": "user", "content": prompt},
        ],
    )
    code = extract_python(response.output_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code.rstrip() + "\n", encoding="utf-8")
    return code


def main() -> None:
    args = parse_args()
    principles_path = Path(args.principles)
    output_path = Path(args.output)
    generate_strategy_code(
        principles_path=principles_path,
        output_path=output_path,
        class_name=args.class_name,
        model=args.model,
    )
    print(f"Generated strategy module: {output_path}")


if __name__ == "__main__":
    main()
