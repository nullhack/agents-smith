"""CLI entrypoint for smith — invoked via `python -m smith`."""

import argparse
import importlib.metadata


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    meta = importlib.metadata.metadata("smith")
    parser = argparse.ArgumentParser(
        prog="smith",
        description=meta["Summary"],
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"smith {meta['Version']}",
    )
    return parser


def main() -> None:
    """Run the application."""
    build_parser().parse_args()


if __name__ == "__main__":
    main()
