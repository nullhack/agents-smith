from pathlib import Path

from smith.core import resolve_source


def test_source_resolution_cli_flag(tmp_path: Path) -> None:
    """
    Given a project with [tool.smith] source = "github:myorg/templates"
    in pyproject.toml
    When the developer runs smith clone --source github:other/repo
    Then the source resolves to "github:other/repo"
    """
    (tmp_path / "pyproject.toml").write_text(
        '[tool.smith]\nsource = "github:myorg/templates"\n'
    )
    result = resolve_source("github:other/repo", tmp_path)
    assert result == "github:other/repo"


def test_source_resolution_config_fallback(tmp_path: Path) -> None:
    """
    Given a project with [tool.smith] source = "github:myorg/templates"
    in pyproject.toml
    When the developer runs smith clone without --source
    Then the source resolves to "github:myorg/templates"
    """
    (tmp_path / "pyproject.toml").write_text(
        '[tool.smith]\nsource = "github:myorg/templates"\n'
    )
    result = resolve_source(None, tmp_path)
    assert result == "github:myorg/templates"


def test_source_resolution_default(tmp_path: Path) -> None:
    """
    Given a project with no [tool.smith] section in pyproject.toml
    When the developer runs smith clone without --source
    Then the source resolves to "github:nullhack/temple8"
    """
    result = resolve_source(None, tmp_path)
    assert result == "github:nullhack/temple8"
