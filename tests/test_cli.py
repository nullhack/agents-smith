"""Tests for smith.cli module."""

from unittest.mock import MagicMock, patch

from smith.cli import build_parser, main


class TestBuildParser:
    def test_clone_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["clone", "--source", "github:user/repo"])
        assert args.command == "clone"
        assert args.source == "github:user/repo"
        assert not args.overwrite

    def test_clone_with_overwrite(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["clone", "--overwrite"])
        assert args.overwrite is True

    def test_purge_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["purge"])
        assert args.command == "purge"

    def test_no_command_prints_help(self, capsys) -> None:
        exit_code = main([])
        assert exit_code == 1


class TestHandleClone:
    @patch("smith.cli.clone")
    @patch("smith.cli.resolve_source")
    def test_calls_clone(self, mock_resolve: MagicMock, mock_clone: MagicMock) -> None:
        mock_resolve.return_value = "github:nullhack/temple8"
        exit_code = main(["clone"])
        mock_clone.assert_called_once()
        assert exit_code == 0

    @patch("smith.cli.clone", side_effect=RuntimeError("boom"))
    @patch("smith.cli.resolve_source", return_value="github:nullhack/temple8")
    def test_error_returns_1(
        self, mock_resolve: MagicMock, mock_clone: MagicMock
    ) -> None:
        exit_code = main(["clone"])
        assert exit_code == 1


class TestHandlePurge:
    @patch("smith.cli.purge", return_value=[("AGENTS.md",)])
    def test_calls_purge(self, mock_purge: MagicMock) -> None:
        exit_code = main(["purge"])
        mock_purge.assert_called_once()
        assert exit_code == 0
