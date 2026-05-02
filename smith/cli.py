"""CLI entry point for the smith command-line tool."""

import argparse
import sys
from pathlib import Path

from smith.core import clone, purge, resolve_source


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the smith CLI."""
    parser = argparse.ArgumentParser(
        prog="smith",
        description="Clone AI agent configurations into any project",
    )
    parser.add_argument("--version", action="version", version=_get_version())

    subparsers = parser.add_subparsers(dest="command")

    clone_parser = subparsers.add_parser(
        "clone", help="Clone agentic files into a project"
    )
    clone_parser.add_argument(
        "--source",
        help="Template source (github:user/repo, local path, or URL to zip/tar.gz)",
    )
    clone_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files and directories",
    )
    clone_parser.set_defaults(func=_handle_clone)

    purge_parser = subparsers.add_parser(
        "purge", help="Purge agentic files from a project"
    )
    purge_parser.set_defaults(func=_handle_purge)

    return parser


def _get_version() -> str:
    """Return the current smith version string."""
    try:
        from importlib.metadata import metadata

        meta = metadata("agents-smith")
        return f"smith {meta['Version']}"
    except Exception:
        return "smith 2.0.0"


def _handle_clone(args: argparse.Namespace) -> int:
    """Handle the clone sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    try:
        source = resolve_source(getattr(args, "source", None), project_dir)
        clone(project_dir, source, overwrite=args.overwrite)
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def _handle_purge(args: argparse.Namespace) -> int:
    """Handle the purge sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    try:
        removed = purge(project_dir)
        if removed:
            for p in removed:
                print(f"Removed: {p}")
        else:
            print("Nothing to purge (no smith-managed section found)")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def main(argv: list[str] | None = None) -> int:
    """Run the smith CLI and return an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)
