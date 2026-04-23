"""Tests for unrecognised arguments story."""

import subprocess
import sys


def test_cli_entrypoint_e7f8a9b0() -> None:
    """
    Given: the application package is installed
    When: the user runs `python -m smith --unknown-flag`
    Then: the process exits with code 2
    """
    result = subprocess.run(
        [sys.executable, "-m", "smith", "--unknown-flag"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_cli_entrypoint_b1c2d3e4() -> None:
    """
    Given: the application package is installed
    When: the user runs `python -m smith` with no arguments
    Then: the process exits with code 0
    """
    result = subprocess.run(
        [sys.executable, "-m", "smith"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
