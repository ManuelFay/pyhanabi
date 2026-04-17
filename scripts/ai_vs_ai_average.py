#!/usr/bin/env python3
"""Run same-strategy AI-vs-AI Hanabi experiments with progress output."""

import argparse
from pathlib import Path
import statistics
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hanabi

# Keep this list to six broadly useful built-in strategies.
DEFAULT_STRATEGIES = ["random", "inner", "outer", "self", "intentional", "full"]
SPINNER_FRAMES = "|/-\\"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run sequential Hanabi experiments where both players use the same "
            "strategy, and report aggregate stats."
        )
    )
    parser.add_argument(
        "--games",
        type=int,
        default=100,
        help="Number of games per strategy (default: 100)",
    )
    parser.add_argument(
        "--strategies",
        nargs="*",
        default=DEFAULT_STRATEGIES,
        help=(
            "Strategies to test sequentially. Defaults to: "
            + ", ".join(DEFAULT_STRATEGIES)
        ),
    )
    return parser.parse_args()


def render_progress(label, current, total, width=28):
    if total <= 0:
        total = 1
    ratio = current / float(total)
    filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    percent = int(ratio * 100)
    return f"\r{label:<12} [{bar}] {current:>3}/{total:<3} ({percent:>3}%)"


def run_single_game(strategy, seed):
    hanabi.random.seed(seed)
    players = [hanabi.make_player(strategy, 0), hanabi.make_player(strategy, 1)]
    game = hanabi.Game(players, hanabi.NullStream())
    return game.run()


def run_single_game_with_spinner(strategy, game_idx, games):
    result = {"score": None, "error": None}

    def worker():
        try:
            result["score"] = run_single_game(strategy, game_idx)
        except Exception as exc:  # surfaced after join
            result["error"] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    start_time = time.time()
    frame = 0
    while thread.is_alive():
        elapsed = time.time() - start_time
        spinner = SPINNER_FRAMES[frame % len(SPINNER_FRAMES)]
        status = (
            f"\r{strategy:<12} game {game_idx:>3}/{games:<3} {spinner} "
            f"elapsed {elapsed:>5.1f}s"
        )
        sys.stdout.write(status)
        sys.stdout.flush()
        frame += 1
        time.sleep(0.2)

    thread.join()
    if result["error"] is not None:
        raise result["error"]

    return result["score"]


def run_same_strategy(strategy, games):
    points = []
    for game_idx in range(1, games + 1):
        points.append(run_single_game_with_spinner(strategy, game_idx, games))
        sys.stdout.write(render_progress(strategy, game_idx, games))
        sys.stdout.flush()
    sys.stdout.write("\n")
    return {
        "strategy": strategy,
        "average": statistics.mean(points),
        "stddev": statistics.stdev(points) if len(points) > 1 else 0.0,
        "min": min(points),
        "max": max(points),
    }


def main():
    args = parse_args()
    if args.games < 1:
        raise ValueError("--games must be >= 1")

    available = set(hanabi.get_playertypes().keys())
    unknown = [s for s in args.strategies if s not in available]
    if unknown:
        raise ValueError(
            "Unknown strategies: %s. Available strategies: %s"
            % (", ".join(unknown), ", ".join(sorted(available)))
        )

    print("Running same-strategy AI-vs-AI experiments")
    print("Strategies:", ", ".join(args.strategies))
    print("Games per strategy:", args.games)
    print("(Progress bar updates per completed game; spinner shows in-flight game activity.)")
    print()

    results = []
    for strategy in args.strategies:
        results.append(run_same_strategy(strategy, args.games))

    print("\nSummary (sorted by average score desc):")
    for row in sorted(results, key=lambda r: r["average"], reverse=True):
        print(
            "- {strategy:12} avg={average:.3f} stddev={stddev:.3f} range={min}-{max}".format(
                **row
            )
        )


if __name__ == "__main__":
    main()
