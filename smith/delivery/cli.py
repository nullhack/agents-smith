"""CLI entry point for the smith command-line tool."""

import argparse
import sys
from pathlib import Path

from smith.application.connect import ConnectUseCase
from smith.application.disconnect import DisconnectUseCase
from smith.application.status import StatusUseCase
from smith.application.update import UpdateUseCase
from smith.domain.ports import TemplateSourceError
from smith.domain.value_objects import TemplateSource

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the smith CLI."""
    parser = argparse.ArgumentParser(
        prog="smith", description="Connect AI agent configurations to any project"
    )
    parser.add_argument("--version", action="version", version=_get_version())

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    connect_parser = subparsers.add_parser(
        "connect", help="Connect agentic files to a project"
    )
    connect_parser.add_argument(
        "--from",
        dest="source",
        help="Template source (bundled:agents-smith, local path, or URL)",
    )
    connect_parser.add_argument(
        "--overwrite",
        action="store_true",
        dest="overwrite",
        help="Replace existing agentic files without prompting",
    )
    connect_parser.set_defaults(func=handle_connect)

    disconnect_parser = subparsers.add_parser(
        "disconnect", help="Disconnect agentic files from a project"
    )
    disconnect_parser.set_defaults(func=handle_disconnect)

    update_parser = subparsers.add_parser("update", help="Update agentic files")
    update_parser.add_argument(
        "--from",
        dest="source",
        help="Template source (bundled:agents-smith, local path, or URL)",
    )
    update_parser.set_defaults(func=handle_update)

    status_parser = subparsers.add_parser("status", help="Show connection status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    status_parser.set_defaults(func=handle_status)

    return parser


def _get_version() -> str:
    """Return the current smith version string."""
    try:
        from importlib.metadata import metadata

        meta = metadata("agents-smith")
        return f"smith {meta['Version']}"
    except Exception:
        return "smith 0.1.0"


def _parse_source(source_arg: str | None) -> TemplateSource:
    """Parse a source argument string into a TemplateSource value object."""
    if source_arg is None:
        return TemplateSource(kind="bundled", location="agents-smith")
    if source_arg.startswith("/"):
        return TemplateSource(kind="local", location=source_arg)
    if source_arg.startswith("http://") or source_arg.startswith("https://"):
        return TemplateSource(kind="url", location=source_arg)
    if ":" in source_arg:
        kind, _, location = source_arg.partition(":")
        return TemplateSource(kind=kind, location=location)  # type: ignore[arg-type]
    return TemplateSource(kind="local", location=source_arg)


def handle_connect(args: argparse.Namespace) -> int:
    """Handle the ``connect`` sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    source = _parse_source(getattr(args, "source", None))
    overwrite = getattr(args, "overwrite", False)
    try:
        ConnectUseCase(project_dir=project_dir).execute(
            source=source, overwrite=overwrite
        )
        return EXIT_SUCCESS
    except TemplateSourceError as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR


def handle_disconnect(args: argparse.Namespace) -> int:
    """Handle the ``disconnect`` sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    try:
        DisconnectUseCase(project_dir=project_dir).execute()
        return EXIT_SUCCESS
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR


def handle_update(args: argparse.Namespace) -> int:
    """Handle the ``update`` sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    source = _parse_source(getattr(args, "source", None))
    try:
        UpdateUseCase(project_dir=project_dir).execute(
            source=source if args.source else None
        )
        return EXIT_SUCCESS
    except TemplateSourceError as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR


def handle_status(args: argparse.Namespace) -> int:
    """Handle the ``status`` sub-command."""
    project_dir = Path(getattr(args, "project_dir", ".")).resolve()
    try:
        status = StatusUseCase(project_dir=project_dir).execute()
        if getattr(args, "json", False):
            import json

            sys.stdout.write(json.dumps(status.to_dict(), indent=2) + "\n")
        else:
            sys.stdout.write(f"State: {status.state.value}\n")
            if status.source:
                sys.stdout.write(
                    f"Source: {status.source.kind}:{status.source.location}\n"
                )
            if status.present_files:
                sys.stdout.write("Present files:\n")
                for f in status.present_files:
                    sys.stdout.write(f"  {f}\n")
            if status.missing_files:
                sys.stdout.write("Missing files:\n")
                for f in status.missing_files:
                    sys.stdout.write(f"  {f}\n")
        return EXIT_SUCCESS
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return EXIT_ERROR


def main(argv: list[str] | None = None) -> int:
    """Run the smith CLI and return an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return EXIT_ERROR
    return args.func(args)
