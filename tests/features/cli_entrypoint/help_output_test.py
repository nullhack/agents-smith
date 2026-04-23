"""Tests for help output story."""

import importlib.metadata
import subprocess
import sys


def test_cli_entrypoint_c1a2b3d4() -> None:
    """
    Given: the application package is installed
    When: the user runs `python -m smith --help`
    Then: the output contains the application name "smith"
    And: the output contains the tagline
    And: the process exits with code 0
    """
    tagline = importlib.metadata.metadata("smith")["Summary"]
    result = subprocess.run(
        [sys.executable, "-m", "smith", "--help"],
        capture_output=True,
        text=True,
    )
    assert "smith" in result.stdout
    unwrapped = result.stdout.replace("\n", " ")
    assert tagline in unwrapped
    assert result.returncode == 0


def test_cli_entrypoint_e5f6a7b8() -> None:
    """
    Given: the application package is installed
    When: the user runs `python -m smith --help`
    Then: the output contains "--help"
    And: the output contains "--version"
    """
    result = subprocess.run(
        [sys.executable, "-m", "smith", "--help"],
        capture_output=True,
        text=True,
    )
    assert "--help" in result.stdout
    assert "--version" in result.stdout
