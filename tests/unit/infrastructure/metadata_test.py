from pathlib import Path

from smith.domain.value_objects import TemplateSource
from smith.infrastructure.gitignore import GitignoreManager
from smith.infrastructure.metadata import SectionMetadata


class TestSectionMetadata:
    def test_save_source_stores_in_gitignore_header(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/"])
        meta = SectionMetadata(tmp_path)
        meta.save_source(TemplateSource(kind="bundled", location="agents-smith"))
        content = (tmp_path / ".gitignore").read_text()
        assert "source:bundled:agents-smith" in content

    def test_load_source_returns_template_source(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/"])
        meta = SectionMetadata(tmp_path)
        meta.save_source(TemplateSource(kind="bundled", location="agents-smith"))
        source = meta.load_source()
        assert source is not None
        assert source.kind == "bundled"
        assert source.location == "agents-smith"

    def test_load_source_returns_none_when_no_section(self, tmp_path: Path) -> None:
        meta = SectionMetadata(tmp_path)
        assert meta.load_source() is None

    def test_save_source_preserves_patterns(self, tmp_path: Path) -> None:
        gi = GitignoreManager(tmp_path)
        gi.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
        meta = SectionMetadata(tmp_path)
        meta.save_source(TemplateSource(kind="local", location="/path/to/tmpl"))
        patterns = gi.get_patterns()
        assert "AGENTS.md" in patterns
        assert ".opencode/" in patterns
