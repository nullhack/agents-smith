from pathlib import Path

from smith.core import _is_allowed


def test_allowed_topics_exact_match() -> None:
    """
    Given a relative path "AGENTS.md"
    When the filter checks if it is allowed
    Then it returns true
    """
    assert _is_allowed(Path("AGENTS.md"))


def test_allowed_topics_directory_prefix() -> None:
    """
    Given a relative path ".opencode/agents/default.md"
    When the filter checks if it is allowed
    Then it returns true
    """
    assert _is_allowed(Path(".opencode/agents/default.md"))


def test_allowed_topics_rejects_random() -> None:
    """
    Given a relative path "README.md"
    When the filter checks if it is allowed
    Then it returns false
    """
    assert not _is_allowed(Path("README.md"))


def test_allowed_topics_rejects_src() -> None:
    """
    Given a relative path "src/main.py"
    When the filter checks if it is allowed
    Then it returns false
    """
    assert not _is_allowed(Path("src/main.py"))
