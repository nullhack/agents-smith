"""Tests for smith.core module."""

from pathlib import Path

import pytest

from smith.core import (
    FileSpec,
    _detect_top_dir,
    _is_allowed,
    _top_level_patterns,
    clone,
    fetch,
    purge,
    resolve_source,
)


class TestIsAllowed:
    def test_agents_md(self) -> None:
        assert _is_allowed(Path("AGENTS.md"))

    def test_opencode_nested(self) -> None:
        assert _is_allowed(Path(".opencode/agents/default.md"))

    def test_flowr_nested(self) -> None:
        assert _is_allowed(Path(".flowr/flows/build.yaml"))

    def test_templates_nested(self) -> None:
        assert _is_allowed(Path(".templates/docs/adr.md.template"))

    def test_rejects_random_file(self) -> None:
        assert not _is_allowed(Path("README.md"))

    def test_rejects_src_directory(self) -> None:
        assert not _is_allowed(Path("src/main.py"))


class TestTopLevelPatterns:
    def test_derives_patterns(self) -> None:
        specs = [
            FileSpec(Path("AGENTS.md"), b""),
            FileSpec(Path(".opencode/agents/default.md"), b""),
            FileSpec(Path(".flowr/flows/build.yaml"), b""),
        ]
        assert _top_level_patterns(specs) == [".flowr/", ".opencode/", "AGENTS.md"]


class TestDetectTopDir:
    def test_single_top_dir(self) -> None:
        names = ["temple8-main/AGENTS.md", "temple8-main/.opencode/agents/default.md"]
        assert _detect_top_dir(names) == "temple8-main"

    def test_multiple_top_dirs(self) -> None:
        names = ["foo/a.txt", "bar/b.txt"]
        assert _detect_top_dir(names) is None

    def test_root_level_file(self) -> None:
        names = ["AGENTS.md", "src/main.py"]
        assert _detect_top_dir(names) is None


class TestResolveSource:
    def test_cli_arg_takes_precedence(self, tmp_path: Path) -> None:
        result = resolve_source("github:user/repo", tmp_path)
        assert result == "github:user/repo"

    def test_reads_from_pyproject_toml(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[tool.smith]\nsource = "github:myorg/templates"\n'
        )
        result = resolve_source(None, tmp_path)
        assert result == "github:myorg/templates"

    def test_returns_default_when_no_config(self, tmp_path: Path) -> None:
        result = resolve_source(None, tmp_path)
        assert result == "github:nullhack/temple8"

    def test_cli_arg_overrides_pyproject(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[tool.smith]\nsource = "github:myorg/templates"\n'
        )
        result = resolve_source("github:other/repo", tmp_path)
        assert result == "github:other/repo"


class TestFetchLocal:
    def test_fetches_local_directory(self, tmp_path: Path) -> None:
        template = tmp_path / "template"
        template.mkdir()
        (template / "AGENTS.md").write_text("# agents")
        opencode = template / ".opencode" / "agents"
        opencode.mkdir(parents=True)
        (opencode / "default.md").write_text("default agent")
        src = template / "src"
        src.mkdir()
        (src / "main.py").write_text("print('hello')")
        specs = fetch(str(template))
        rel_paths = [str(s.relative_path) for s in specs]
        assert "AGENTS.md" in rel_paths
        assert any(".opencode" in p for p in rel_paths)
        assert not any("src" in p for p in rel_paths)

    def test_raises_on_missing_directory(self) -> None:
        with pytest.raises(RuntimeError, match="not found"):
            fetch("/nonexistent/path")

    def test_raises_on_no_matching_files(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        (empty / "README.md").write_text("hello")
        with pytest.raises(RuntimeError, match="No matching files"):
            fetch(str(empty))


class TestClone:
    def test_clone_writes_files_and_gitignore(self, tmp_path: Path) -> None:
        template = tmp_path / "template"
        template.mkdir()
        (template / "AGENTS.md").write_text("# agents")
        opencode = template / ".opencode" / "agents"
        opencode.mkdir(parents=True)
        (opencode / "default.md").write_text("default")
        clone(tmp_path / "project", str(template))
        project = tmp_path / "project"
        assert (project / "AGENTS.md").read_text() == "# agents"
        assert (
            project / ".opencode" / "agents" / "default.md"
        ).read_text() == "default"
        gitignore = (project / ".gitignore").read_text()
        assert "# smith managed" in gitignore
        assert "AGENTS.md" in gitignore
        assert ".opencode/" in gitignore

    def test_clone_skips_existing_without_overwrite(self, tmp_path: Path) -> None:
        template = tmp_path / "template"
        template.mkdir()
        (template / "AGENTS.md").write_text("new content")
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("old content")
        clone(project, str(template), overwrite=False)
        assert (project / "AGENTS.md").read_text() == "old content"

    def test_clone_overwrites_with_flag(self, tmp_path: Path) -> None:
        template = tmp_path / "template"
        template.mkdir()
        (template / "AGENTS.md").write_text("new content")
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("old content")
        clone(project, str(template), overwrite=True)
        assert (project / "AGENTS.md").read_text() == "new content"

    def test_clone_skips_existing_directory(self, tmp_path: Path) -> None:
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


class TestPurge:
    def test_purge_removes_files_and_dirs(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# agents")
        opencode = project / ".opencode"
        opencode.mkdir()
        (opencode / "agents.md").write_text("agent")
        (project / ".gitignore").write_text(
            "# smith managed\nAGENTS.md\n.opencode/\n# end smith managed\n"
        )
        removed = purge(project)
        assert not (project / "AGENTS.md").exists()
        assert not (project / ".opencode").exists()
        assert Path("AGENTS.md") in removed

    def test_purge_keeps_gitignore_section(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# agents")
        (project / ".gitignore").write_text(
            "# smith managed\nAGENTS.md\n# end smith managed\n"
        )
        purge(project)
        gitignore = (project / ".gitignore").read_text()
        assert "# smith managed" in gitignore
        assert "# end smith managed" in gitignore

    def test_purge_no_section_is_noop(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# agents")
        removed = purge(project)
        assert removed == []
        assert (project / "AGENTS.md").exists()

    def test_purge_only_deletes_listed_patterns(self, tmp_path: Path) -> None:
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
