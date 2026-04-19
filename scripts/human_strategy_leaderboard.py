#!/usr/bin/env python3
"""Evaluate human-principles-generated strategies in self-play and write a leaderboard."""

import argparse
import json
from pathlib import Path
import statistics
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import hanabi


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate self-play for human-principles strategies.")
    parser.add_argument("--manifest", default="human_strategies/manifest.json", help="Manifest JSON path")
    parser.add_argument("--games", type=int, default=200, help="Games per strategy (default: 200)")
    parser.add_argument(
        "--output",
        default="docs/human_strategy_leaderboard.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def run_self_play(strategy_alias, games):
    points = []
    perfect = 0
    for seed in range(1, games + 1):
        hanabi.random.seed(seed)
        players = [hanabi.make_player(strategy_alias, 0), hanabi.make_player(strategy_alias, 1)]
        if any(p is None for p in players):
            raise ValueError(f"Unknown strategy alias: {strategy_alias}")
        game = hanabi.Game(players, hanabi.NullStream())
        score = game.run()
        points.append(score)
        if score == 25:
            perfect += 1
    return {
        "mean": statistics.mean(points),
        "perfect": perfect,
        "games": games,
        "min": min(points),
        "max": max(points),
    }


def to_markdown(rows, games, manifest_path):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = []
    lines.append("# Human strategy self-play leaderboard")
    lines.append("")
    lines.append(f"Generated: `{stamp}` (UTC)")
    lines.append(f"Manifest: `{manifest_path}`")
    lines.append(f"Games per strategy: `{games}`")
    lines.append("")
    lines.append("| Rank | Strategy | Mean score | Perfect games | Perfect rate | Range | Design doc |")
    lines.append("|---:|---|---:|---:|---:|---:|---|")
    sorted_rows = sorted(rows, key=lambda row: row["metrics"]["mean"], reverse=True)
    for rank, row in enumerate(sorted_rows, 1):
        m = row["metrics"]
        rate = (100.0 * m["perfect"] / float(m["games"]))
        lines.append(
            "| {rank} | `{alias}` | {mean:.3f} | {perfect}/{games} | {rate:.1f}% | {minv}-{maxv} | `{doc}` |".format(
                rank=rank,
                alias=row["strategy_alias"],
                mean=m["mean"],
                perfect=m["perfect"],
                games=m["games"],
                rate=rate,
                minv=m["min"],
                maxv=m["max"],
                doc=row["principles"],
            )
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main():
    args = parse_args()
    manifest_path = ROOT / args.manifest
    output_path = ROOT / args.output

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for entry in manifest:
        strategy_alias = entry["strategy_alias"]
        metrics = run_self_play(strategy_alias, args.games)
        rows.append({
            "strategy_alias": strategy_alias,
            "principles": entry["principles"],
            "metrics": metrics,
        })
        print(
            f"{strategy_alias}: mean={metrics['mean']:.3f}, perfect={metrics['perfect']}/{metrics['games']}, range={metrics['min']}-{metrics['max']}"
        )

    md = to_markdown(rows, args.games, args.manifest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    print(f"Wrote leaderboard: {output_path}")


if __name__ == "__main__":
    main()
