from pathlib import Path

from smith.core import clone


def test_clone_writes_and_tracks(tmp_path: Path) -> None:
    """
    Given a template source containing AGENTS.md and .opencode/agents/default.md
    When the developer runs clone on a project directory
    Then AGENTS.md and .opencode/agents/default.md are written to the project
    And .gitignore contains a "# smith managed" section listing
    "AGENTS.md" and ".opencode/"
    """
    template = tmp_path / "template"
    template.mkdir()
    (template / "AGENTS.md").write_text("# agents")
    opencode = template / ".opencode" / "agents"
    opencode.mkdir(parents=True)
    (opencode / "default.md").write_text("default")

    project = tmp_path / "project"
    project.mkdir()
    clone(project, str(template))

    assert (project / "AGENTS.md").read_text() == "# agents"
    assert (project / ".opencode" / "agents" / "default.md").read_text() == "default"

    gitignore = (project / ".gitignore").read_text()
    assert "# smith managed" in gitignore
    assert "AGENTS.md" in gitignore
    assert ".opencode/" in gitignore


def test_clone_skips_existing(tmp_path: Path) -> None:
    """
    Given a project directory with AGENTS.md containing "old content"
    And a template source with AGENTS.md containing "new content"
    When the developer runs clone without --overwrite
    Then AGENTS.md retains "old content"
    """
    template = tmp_path / "template"
    template.mkdir()
    (template / "AGENTS.md").write_text("new content")

    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("old content")

    clone(project, str(template), overwrite=False)
    assert (project / "AGENTS.md").read_text() == "old content"


def test_clone_skips_existing_directory(tmp_path: Path) -> None:
    """
    Given a project directory with .opencode/existing.md
    And a template source with .opencode/agents/default.md
    When the developer runs clone without --overwrite
    Then .opencode/existing.md is preserved
    And .opencode/agents/default.md is NOT written
    """
    template = tmp_path / "template"
    template.mkdir()
    opencode = template / ".opencode" / "agents"
    opencode.mkdir(parents=True)
    (opencode / "default.md").write_text("default")

    project = tmp_path / "project"
    project.mkdir()
    existing = project / ".opencode"
    existing.mkdir()
    (existing / "existing.md").write_text("existing")

    clone(project, str(template), overwrite=False)
    assert (project / ".opencode" / "existing.md").read_text() == "existing"
    assert not (project / ".opencode" / "agents" / "default.md").exists()


def test_clone_overwrites_with_flag(tmp_path: Path) -> None:
    """
    Given a project directory with AGENTS.md containing "old content"
    And a template source with AGENTS.md containing "new content"
    When the developer runs clone with --overwrite
    Then AGENTS.md contains "new content"
    """
    template = tmp_path / "template"
    template.mkdir()
    (template / "AGENTS.md").write_text("new content")

    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("old content")

    clone(project, str(template), overwrite=True)
    assert (project / "AGENTS.md").read_text() == "new content"
