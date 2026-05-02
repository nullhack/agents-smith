from pathlib import Path

from smith.core import purge


def test_purge_removes_tracked(tmp_path: Path) -> None:
    """
    Given a project with AGENTS.md, .opencode/ directory, and .gitignore containing
    "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed"
    When the developer runs purge
    Then AGENTS.md is deleted
    And .opencode/ directory is deleted
    And the managed section in .gitignore is preserved
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# agents")
    opencode = project / ".opencode"
    opencode.mkdir()
    (opencode / "agents.md").write_text("agent")
    (project / ".gitignore").write_text(
        "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed\n"
    )

    purge(project)

    assert not (project / "AGENTS.md").exists()
    assert not (project / ".opencode").exists()
    gitignore = (project / ".gitignore").read_text()
    assert "# smith managed" in gitignore
    assert "# end smith managed" in gitignore


def test_purge_preserves_untracked(tmp_path: Path) -> None:
    """
    Given a project with AGENTS.md, README.md, and .gitignore containing
    "# smith managed\nAGENTS.md\n# end smith managed"
    When the developer runs purge
    Then AGENTS.md is deleted
    And README.md is preserved
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# agents")
    (project / "README.md").write_text("# readme")
    (project / ".gitignore").write_text(
        "# smith managed\nAGENTS.md\n# end smith managed\n"
    )

    purge(project)

    assert not (project / "AGENTS.md").exists()
    assert (project / "README.md").exists()


def test_purge_no_section_noop(tmp_path: Path) -> None:
    """
    Given a project with AGENTS.md but no smith-managed section in .gitignore
    When the developer runs purge
    Then no files are deleted
    And AGENTS.md is preserved
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# agents")

    removed = purge(project)
    assert removed == []
    assert (project / "AGENTS.md").exists()
