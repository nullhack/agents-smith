"""Unit tests for smith.__main__ — in-process coverage."""

import argparse
import sys

import pytest

from smith.delivery.cli import build_parser, main


def test_build_parser_returns_argument_parser() -> None:
    """build_parser returns a configured ArgumentParser instance."""
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_description_is_set() -> None:
    """build_parser sets a description for the CLI."""
    parser = build_parser()
    assert parser.description is not None


def test_main_exits_0_with_no_args(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() with no argv exits cleanly (code 0)."""
    monkeypatch.setattr(sys, "argv", ["smith"])
    main()


def test_main_exits_0_with_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() with --help exits with SystemExit(0)."""
    monkeypatch.setattr(sys, "argv", ["smith", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_exits_0_with_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """main() with --version exits with SystemExit(0)."""
    monkeypatch.setattr(sys, "argv", ["smith", "--version"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
