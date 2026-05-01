from pathlib import Path

from smith.infrastructure.gitignore import END_MARKER, START_MARKER, GitignoreManager


class TestGitignoreManager:
    def test_add_section_creates_gitignore(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/"])
        content = (tmp_path / ".gitignore").read_text()
        assert START_MARKER in content
        assert END_MARKER in content
        assert "AGENTS.md" in content
        assert ".opencode/" in content

    def test_has_section_returns_true_when_present(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md"])
        assert gi.has_section() is True

    def test_has_section_returns_false_when_absent(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        assert gi.has_section() is False

    def test_get_patterns_returns_patterns(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
        patterns = gi.get_patterns()
        assert "AGENTS.md" in patterns
        assert ".opencode/" in patterns
        assert ".templates/" in patterns
        assert ".flowr/" in patterns

    def test_get_patterns_returns_empty_when_no_section(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        assert gi.get_patterns() == []

    def test_add_section_appends_to_existing_gitignore(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text("node_modules/\n*.log\n")
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md"])
        content = (tmp_path / ".gitignore").read_text()
        assert "node_modules/" in content
        assert START_MARKER in content

    def test_add_section_replaces_existing_section(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/"])
        gi.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
        content = (tmp_path / ".gitignore").read_text()
        assert content.count(START_MARKER) == 1
        patterns = gi.get_patterns()
        assert ".templates/" in patterns
        assert ".flowr/" in patterns
