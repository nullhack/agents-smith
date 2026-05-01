from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from smith.domain.ports import TemplateSourceError
from smith.domain.value_objects import TemplateSource
from smith.infrastructure.template_source import (
    BundledTemplateSource,
    LocalTemplateSource,
    TemplateSourceAdapter,
    UrlTemplateSource,
    _collect_specs_from_directory,
    _is_agentic_path,
)


class TestBundledTemplateSource:
    def test_resolve_returns_agentic_files(self) -> None:
        source = BundledTemplateSource()
        specs = source.resolve()
        paths = [s.relative_path for s in specs]
        assert any(str(p) == "AGENTS.md" for p in paths)
        assert any(str(p).startswith(".opencode/") for p in paths)

    def test_resolve_filters_non_agentic_files(self) -> None:
        source = BundledTemplateSource()
        specs = source.resolve()
        for spec in specs:
            assert _is_agentic_path(spec.relative_path), (
                f"Non-agentic file in bundle: {spec.relative_path}"
            )

    def test_resolve_raises_when_data_missing(self) -> None:
        source = BundledTemplateSource()
        with (
            patch(
                "smith.infrastructure.template_source.importlib.resources.files",
                side_effect=ModuleNotFoundError("smith.data"),
            ),
            pytest.raises(TemplateSourceError, match="Failed to locate"),
        ):
            source.resolve()

    def test_gitignore_patterns_returns_list(self) -> None:
        source = BundledTemplateSource()
        patterns = source.gitignore_patterns()
        assert isinstance(patterns, list)
        assert "AGENTS.md" in patterns
        assert ".opencode/" in patterns
        assert ".templates/" in patterns
        assert ".flowr/" in patterns


class TestLocalTemplateSource:
    def test_resolve_from_directory(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"# Local agents\n")
        (tmp_path / ".opencode").mkdir()
        (tmp_path / ".opencode" / "config.yaml").write_bytes(b"key: local\n")
        source = LocalTemplateSource(tmp_path)
        specs = source.resolve()
        paths = [s.relative_path for s in specs]
        assert Path("AGENTS.md") in paths

    def test_gitignore_patterns_from_directory(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"# Local\n")
        source = LocalTemplateSource(tmp_path)
        patterns = source.gitignore_patterns()
        assert isinstance(patterns, list)
        assert "AGENTS.md" in patterns

    def test_resolve_nonexistent_directory_raises(self, tmp_path: Path) -> None:
        source = LocalTemplateSource(tmp_path / "nonexistent")
        with pytest.raises(TemplateSourceError):
            source.resolve()


class TestUrlTemplateSource:
    def test_resolve_downloads_tar_gz(self, tmp_path: Path) -> None:
        import io
        import tarfile

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "AGENTS.md").write_bytes(b"# URL agents\n")
        (src_dir / ".opencode").mkdir()
        (src_dir / ".opencode" / "agents").mkdir()
        (src_dir / ".opencode" / "agents" / "po.md").write_bytes(b"# PO\n")
        (src_dir / "README.md").write_bytes(b"# Not agentic\n")

        tar_bytes = io.BytesIO()
        with tarfile.open(fileobj=tar_bytes, mode="w:gz") as tar:
            tar.add(str(src_dir / "AGENTS.md"), arcname="agents-smith/AGENTS.md")
            tar.add(
                str(src_dir / ".opencode"),
                arcname="agents-smith/.opencode",
            )
            tar.add(
                str(src_dir / ".opencode" / "agents"),
                arcname="agents-smith/.opencode/agents",
            )
            tar.add(
                str(src_dir / ".opencode" / "agents" / "po.md"),
                arcname="agents-smith/.opencode/agents/po.md",
            )
            tar.add(str(src_dir / "README.md"), arcname="agents-smith/README.md")
        tar_bytes.seek(0)

        mock_response = MagicMock()
        mock_response.content = tar_bytes.read()
        mock_response.raise_for_status = MagicMock()

        source = UrlTemplateSource("https://example.com/templates.tar.gz")
        with patch("smith.infrastructure.template_source.requests") as mock_req:
            mock_req.get.return_value = mock_response
            mock_req.RequestException = Exception
            specs = source.resolve()

        paths = [s.relative_path for s in specs]
        assert Path("AGENTS.md") in paths
        assert any(str(p).startswith(".opencode/") for p in paths)
        assert not any(str(p) == "README.md" for p in paths)

    def test_resolve_raises_on_download_failure(self) -> None:
        source = UrlTemplateSource("https://example.com/notfound.tar.gz")
        with patch("smith.infrastructure.template_source.requests") as mock_req:
            mock_req.get.side_effect = ConnectionError("network unreachable")
            mock_req.RequestException = ConnectionError
            with pytest.raises(TemplateSourceError, match="Failed to download"):
                source.resolve()

    def test_resolve_raises_on_empty_archive(self, tmp_path: Path) -> None:
        import io
        import tarfile

        tar_bytes = io.BytesIO()
        with tarfile.open(fileobj=tar_bytes, mode="w:gz"):
            pass
        tar_bytes.seek(0)

        mock_response = MagicMock()
        mock_response.content = tar_bytes.read()
        mock_response.raise_for_status = MagicMock()

        source = UrlTemplateSource("https://example.com/empty.tar.gz")
        with patch("smith.infrastructure.template_source.requests") as mock_req:
            mock_req.get.return_value = mock_response
            mock_req.RequestException = Exception
            with pytest.raises(TemplateSourceError):
                source.resolve()

    def test_gitignore_patterns_returns_list(self) -> None:
        source = UrlTemplateSource("https://example.com/templates.tar.gz")
        patterns = source.gitignore_patterns()
        assert patterns == ["AGENTS.md", ".opencode/", ".templates/", ".flowr/"]


class TestTemplateSourceAdapter:
    def test_adapter_delegates_to_bundled(self) -> None:
        adapter = TemplateSourceAdapter(
            TemplateSource(kind="bundled", location="agents-smith"),
        )
        specs = adapter.resolve()
        paths = [s.relative_path for s in specs]
        assert any(str(p) == "AGENTS.md" for p in paths)

    def test_adapter_delegates_gitignore_patterns(self) -> None:
        adapter = TemplateSourceAdapter(
            TemplateSource(kind="bundled", location="agents-smith"),
        )
        patterns = adapter.gitignore_patterns()
        assert "AGENTS.md" in patterns

    def test_adapter_delegates_to_local(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"# Local\n")
        adapter = TemplateSourceAdapter(
            TemplateSource(kind="local", location=str(tmp_path)),
        )
        specs = adapter.resolve()
        assert len(specs) >= 1

    def test_adapter_delegates_to_url(self) -> None:
        with patch("smith.infrastructure.template_source.requests") as mock_req:
            mock_req.get.side_effect = ConnectionError("fail")
            mock_req.RequestException = ConnectionError
            adapter = TemplateSourceAdapter(
                TemplateSource(
                    kind="url",
                    location="https://example.com/templates.tar.gz",
                ),
            )
            with pytest.raises(TemplateSourceError, match="Failed to download"):
                adapter.resolve()

    def test_adapter_raises_on_unknown_kind(self) -> None:
        adapter = TemplateSourceAdapter(
            TemplateSource(kind="unknown", location="test"),  # type: ignore[arg-type]
        )
        with pytest.raises(TemplateSourceError, match="Unknown template source kind"):
            adapter.resolve()


class TestCollectSpecsFromDirectory:
    def test_collects_all_files(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"# Agents\n")
        (tmp_path / ".opencode").mkdir()
        (tmp_path / ".opencode" / "config.yaml").write_bytes(b"key: val\n")
        specs = _collect_specs_from_directory(tmp_path)
        paths = [s.relative_path for s in specs]
        assert Path("AGENTS.md") in paths
        assert Path(".opencode/config.yaml") in paths

    def test_empty_directory_raises(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        specs = _collect_specs_from_directory(empty_dir)
        assert specs == []


class TestIsAgenticPath:
    def test_agents_md(self) -> None:
        assert _is_agentic_path(Path("AGENTS.md")) is True

    def test_opencode_subdir(self) -> None:
        assert _is_agentic_path(Path(".opencode/agents/po.md")) is True

    def test_templates_subdir(self) -> None:
        assert _is_agentic_path(Path(".templates/docs/ADR.template")) is True

    def test_flowr_subdir(self) -> None:
        assert _is_agentic_path(Path(".flowr/flows/main.yaml")) is True

    def test_non_agentic(self) -> None:
        assert _is_agentic_path(Path("README.md")) is False
        assert _is_agentic_path(Path("app/main.py")) is False
        assert _is_agentic_path(Path("pyproject.toml")) is False

    def test_opencode_node_modules_excluded(self) -> None:
        assert (
            _is_agentic_path(Path(".opencode/node_modules/effect/package.json"))
            is False
        )
        assert _is_agentic_path(Path(".opencode/package.json")) is False

    def test_opencode_tools(self) -> None:
        assert _is_agentic_path(Path(".opencode/tools/README.md")) is True
