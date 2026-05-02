"""Tests for smith.gitignore module."""

from pathlib import Path

from smith.gitignore import GitignoreManager


class TestAddSection:
    def test_creates_gitignore_if_missing(self, tmp_path: Path) -> None:
        manager = GitignoreManager(tmp_path)
        manager.add_section(["AGENTS.md", ".opencode/"])
        content = (tmp_path / ".gitignore").read_text()
        assert "# smith managed\n" in content
        assert "AGENTS.md\n" in content
        assert ".opencode/\n" in content
        assert "# end smith managed\n" in content

    def test_appends_to_existing_gitignore(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text("node_modules/\ndist/\n")
        manager = GitignoreManager(tmp_path)
        manager.add_section(["AGENTS.md"])
        content = (tmp_path / ".gitignore").read_text()
        assert "node_modules/" in content
        assert "# smith managed\n" in content
        assert "AGENTS.md\n" in content
        assert "# end smith managed\n" in content

    def test_replaces_existing_section(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text(
            "node_modules/\n# smith managed\nAGENTS.md\n# end smith managed\n"
        )
        manager = GitignoreManager(tmp_path)
        manager.add_section([".opencode/", ".flowr/"])
        content = (tmp_path / ".gitignore").read_text()
        assert "node_modules/\n" in content
        assert "# smith managed\n" in content
        assert ".opencode/\n" in content
        assert ".flowr/\n" in content
        assert "AGENTS.md" not in content
        assert "# end smith managed\n" in content


class TestHasSection:
    def test_returns_false_when_no_gitignore(self, tmp_path: Path) -> None:
        manager = GitignoreManager(tmp_path)
        assert not manager.has_section()

    def test_returns_false_when_no_section(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text("node_modules/\n")
        manager = GitignoreManager(tmp_path)
        assert not manager.has_section()

    def test_returns_true_when_section_exists(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text(
            "# smith managed\nAGENTS.md\n# end smith managed\n"
        )
        manager = GitignoreManager(tmp_path)
        assert manager.has_section()


class TestGetPatterns:
    def test_returns_empty_when_no_section(self, tmp_path: Path) -> None:
        manager = GitignoreManager(tmp_path)
        assert manager.get_patterns() == []

    def test_returns_patterns_from_section(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text(
            "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed\n"
        )
        manager = GitignoreManager(tmp_path)
        patterns = manager.get_patterns()
        assert patterns == ["AGENTS.md", ".opencode/"]

    def test_skips_comments_and_blank_lines(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text(
            "# smith managed\n# a comment\nAGENTS.md\n\n"
            ".opencode/\n# end smith managed\n"
        )
        manager = GitignoreManager(tmp_path)
        patterns = manager.get_patterns()
        assert patterns == ["AGENTS.md", ".opencode/"]
