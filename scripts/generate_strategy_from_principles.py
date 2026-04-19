#!/usr/bin/env python3
"""Generate a Hanabi strategy module from a human-authored principles markdown file."""

import argparse
import os
from pathlib import Path


DEFAULT_MODEL = "gpt-5.4-mini"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate strategy Python code from a principles markdown file.")
    parser.add_argument("principles", help="Path to principles markdown file")
    parser.add_argument("output", help="Path to generated Python strategy module")
    parser.add_argument("--class-name", required=True, help="Class name to emit")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model (default: {DEFAULT_MODEL})")
    return parser.parse_args()


def extract_python(text):
    stripped = text.strip()
    if "```" not in stripped:
        return stripped
    parts = stripped.split("```")
    for block in parts:
        candidate = block.strip()
        if candidate.startswith("python"):
            return candidate[len("python"):].lstrip()
    return stripped


def main():
    args = parse_args()

    principles_path = Path(args.principles)
    output_path = Path(args.output)
    principles_text = principles_path.read_text(encoding="utf-8")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai package is required for generation") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to generate strategy code")

    prompt = f"""
You are generating a new Hanabi strategy implementation.

Constraints:
- Use ONLY the principles in the provided markdown; do not reference or imitate any existing strategy names or modules.
- Output valid Python code only.
- Implement class `{args.class_name}` inheriting from `AbstractStrategy`.
- The class must expose: `__init__`, `get_action`, and optional `inform`.
- Imports allowed: `random`, `from .base import AbstractStrategy`, and symbols from `hanabi`.
- Ensure every returned action is legal from `valid_actions` or constructed from observed legal semantics.
- Include module docstring with source principles path: `{principles_path.as_posix()}`.

Principles markdown:
---
{principles_text}
---
""".strip()

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=args.model,
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": "Return only Python code."},
            {"role": "user", "content": prompt},
        ],
    )
    code = extract_python(response.output_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code.rstrip() + "\n", encoding="utf-8")
    print(f"Generated strategy module: {output_path}")


if __name__ == "__main__":
    main()
