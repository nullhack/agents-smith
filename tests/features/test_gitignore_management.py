from pathlib import Path

from smith.gitignore import GitignoreManager


def test_gitignore_create_section(tmp_path: Path) -> None:
    """
    Given a project directory with no .gitignore file
    When smith adds a section with patterns ["AGENTS.md", ".opencode/"]
    Then .gitignore contains "# smith managed" followed by "AGENTS.md"
    and ".opencode/" and "# end smith managed"
    """
    manager = GitignoreManager(tmp_path)
    manager.add_section(["AGENTS.md", ".opencode/"])

    content = (tmp_path / ".gitignore").read_text()
    assert "# smith managed" in content
    assert "AGENTS.md" in content
    assert ".opencode/" in content
    assert "# end smith managed" in content


def test_gitignore_append_to_existing(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing "node_modules/" and "dist/"
    When smith adds a section with patterns ["AGENTS.md"]
    Then .gitignore preserves "node_modules/" and "dist/" and appends
    the managed section
    """
    (tmp_path / ".gitignore").write_text("node_modules/\ndist/\n")

    manager = GitignoreManager(tmp_path)
    manager.add_section(["AGENTS.md"])

    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content
    assert "dist/" in content
    assert "# smith managed" in content
    assert "AGENTS.md" in content
    assert "# end smith managed" in content


def test_gitignore_replace_existing_section(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing a managed
    section listing "AGENTS.md"
    When smith adds a section with patterns [".opencode/", ".flowr/"]
    Then .gitignore preserves content outside the section and replaces
    the section content with ".opencode/" and ".flowr/",
    removing "AGENTS.md"
    """
    (tmp_path / ".gitignore").write_text(
        "node_modules/\n# smith managed\nAGENTS.md\n# end smith managed\n"
    )

    manager = GitignoreManager(tmp_path)
    manager.add_section([".opencode/", ".flowr/"])

    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content
    assert "# smith managed" in content
    assert ".opencode/" in content
    assert ".flowr/" in content
    assert "AGENTS.md" not in content
    assert "# end smith managed" in content


def test_gitignore_has_section(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing
    "# smith managed\\nAGENTS.md\\n# end smith managed"
    When smith checks for the managed section
    Then it returns true
    """
    (tmp_path / ".gitignore").write_text(
        "# smith managed\nAGENTS.md\n# end smith managed\n"
    )

    manager = GitignoreManager(tmp_path)
    assert manager.has_section()


def test_gitignore_no_section(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing only "node_modules/"
    When smith checks for the managed section
    Then it returns false
    """
    (tmp_path / ".gitignore").write_text("node_modules/\n")

    manager = GitignoreManager(tmp_path)
    assert not manager.has_section()


def test_gitignore_no_file(tmp_path: Path) -> None:
    """
    Given a project directory with no .gitignore file
    When smith checks for the managed section
    Then it returns false
    """
    manager = GitignoreManager(tmp_path)
    assert not manager.has_section()


def test_gitignore_get_patterns(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing
    "# smith managed\\nAGENTS.md\\n.opencode/\\n# end smith managed"
    When smith reads the patterns
    Then it returns ["AGENTS.md", ".opencode/"]
    """
    (tmp_path / ".gitignore").write_text(
        "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed\n"
    )

    manager = GitignoreManager(tmp_path)
    patterns = manager.get_patterns()
    assert patterns == ["AGENTS.md", ".opencode/"]


def test_gitignore_skip_comments_blanks(tmp_path: Path) -> None:
    """
    Given a project directory with .gitignore containing comments and
    blanks in the managed section
    When smith reads the patterns
    Then it returns only non-comment, non-blank lines
    """
    (tmp_path / ".gitignore").write_text(
        "# smith managed\n# a comment\nAGENTS.md\n\n.opencode/\n# end smith managed\n"
    )

    manager = GitignoreManager(tmp_path)
    patterns = manager.get_patterns()
    assert patterns == ["AGENTS.md", ".opencode/"]
