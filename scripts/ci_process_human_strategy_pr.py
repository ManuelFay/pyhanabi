#!/usr/bin/env python3
"""CI helper for human strategy PRs.

Detects changed principles markdown files on a PR branch, generates strategy code,
updates manifest/registry, and regenerates leaderboard scores.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from scripts.generate_strategy_from_principles import generate_strategy_code


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "human_strategies/manifest.json"
REGISTRY_PATH = ROOT / "strategies/__init__.py"


def run(cmd: list[str], *, cwd: Path = ROOT) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}"
        )
    return proc.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process changed human strategy markdown files for CI.")
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Base git ref to diff against (default: origin/main)",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=200,
        help="Games per strategy for leaderboard generation",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.4-mini",
        help="Model used by generation script",
    )
    return parser.parse_args()


def changed_principles_files(base_ref: str) -> list[Path]:
    out = run(["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "human_strategies/*.md"])
    files: list[Path] = []
    for rel in out.splitlines():
        rel = rel.strip()
        if not rel:
            continue
        path = Path(rel)
        if path.name == "README.md":
            continue
        if not path.name.endswith("_principles.md"):
            continue
        files.append(path)
    return files


def slugify(stem: str) -> str:
    slug = stem
    if slug.endswith("_principles"):
        slug = slug[: -len("_principles")]
    slug = slug.replace("_", "-")
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", slug).strip("-").lower()
    return slug


def class_name_from_slug(slug: str) -> str:
    parts = [p for p in slug.split("-") if p]
    return "Human" + "".join(p.capitalize() for p in parts) + "Strategy"


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(data: list[dict]) -> None:
    MANIFEST_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def ensure_registry_entry(module_file: str, class_name: str, alias: str) -> None:
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    module_name = Path(module_file).stem
    import_line = f"from .{module_name} import {class_name}"
    if import_line not in text:
        lines = text.splitlines()
        insert_idx = 0
        for idx, line in enumerate(lines):
            if line.startswith("from ."):
                insert_idx = idx + 1
        lines.insert(insert_idx, import_line)
        text = "\n".join(lines) + "\n"

    alias_line = f'    "{alias}": {class_name},'
    if alias_line not in text:
        marker = "STRATEGY_TYPES = {"
        start = text.find(marker)
        if start == -1:
            raise RuntimeError("Unable to locate STRATEGY_TYPES in strategies/__init__.py")
        close_idx = text.find("}\n", start)
        if close_idx == -1:
            raise RuntimeError("Unable to locate end of STRATEGY_TYPES in strategies/__init__.py")
        text = text[:close_idx] + alias_line + "\n" + text[close_idx:]

    REGISTRY_PATH.write_text(text, encoding="utf-8")


def process_markdown_file(principles_rel: Path, manifest: list[dict], model: str) -> bool:
    principles = principles_rel.as_posix()
    for entry in manifest:
        if entry.get("principles") == principles:
            print(f"Manifest already contains {principles}; skipping manifest/registry add")
            return False

    slug = slugify(principles_rel.stem)
    entry_id = f"human-{slug}"
    alias = entry_id
    module_rel = f"strategies/human_{slug.replace('-', '_')}_strategy.py"
    class_name = class_name_from_slug(slug)

    generate_strategy_code(
        principles_path=ROOT / principles,
        output_path=ROOT / module_rel,
        class_name=class_name,
        model=model,
    )

    manifest.append(
        {
            "id": entry_id,
            "principles": principles,
            "strategy_alias": alias,
            "strategy_module": module_rel,
            "strategy_class": class_name,
        }
    )

    ensure_registry_entry(module_rel, class_name, alias)
    print(f"Added strategy: {alias} ({class_name}) from {principles}")
    return True


def main() -> None:
    args = parse_args()
    changed = changed_principles_files(args.base_ref)
    if not changed:
        print("No changed *_principles.md files detected; nothing to do.")
        return

    manifest = load_manifest()
    mutated = False
    for path in changed:
        mutated = process_markdown_file(path, manifest, args.model) or mutated

    if mutated:
        save_manifest(manifest)

    run(["python", "scripts/human_strategy_leaderboard.py", "--games", str(args.games)])
    print("Leaderboard updated.")


if __name__ == "__main__":
    main()
