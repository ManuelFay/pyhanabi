#!/usr/bin/env python3
"""Run two Hanabi AI agents against each other and report average score."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hanabi


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run AI-vs-AI Hanabi games and print aggregate score statistics. "
            "Defaults to 100 games."
        )
    )
    parser.add_argument(
        "player1",
        nargs="?",
        default="random",
        help="First AI type (default: random)",
    )
    parser.add_argument(
        "player2",
        nargs="?",
        default="random",
        help="Second AI type (default: random)",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=100,
        help="Number of games to run (default: 100)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    hanabi.main([args.player1, args.player2, "--games", str(args.games)])


if __name__ == "__main__":
    main()
