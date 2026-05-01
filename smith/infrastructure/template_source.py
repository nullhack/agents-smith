"""Template source adapters — resolve files from bundled, local, or URL sources."""

import importlib.resources
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path

import requests

from smith.domain.ports import TemplateSourceError
from smith.domain.value_objects import FileSpec, TemplateSource

AGENTIC_FILE_PATTERNS = [
    "AGENTS.md",
    ".opencode/agents/",
    ".opencode/knowledge/",
    ".opencode/skills/",
    ".opencode/tools/",
    ".templates/",
    ".flowr/",
]

GITIGNORE_PATTERNS = ["AGENTS.md", ".opencode/", ".templates/", ".flowr/"]


def _is_agentic_path(path: Path) -> bool:
    """Return whether *path* belongs to an agentic file pattern."""
    path_str = str(path)
    if path_str == "AGENTS.md":
        return True
    return any(path_str.startswith(pattern) for pattern in AGENTIC_FILE_PATTERNS[1:])


def _collect_specs_from_directory(directory: Path) -> list[FileSpec]:
    """Walk *directory* and collect FileSpec for every file found."""
    specs: list[FileSpec] = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(directory)
            specs.append(FileSpec(relative_path=rel, content=full.read_bytes()))
    return specs


class BundledTemplateSource:
    """Resolve templates shipped inside the ``smith.data`` package."""

    def resolve(self) -> list[FileSpec]:
        """Return FileSpec list for every agentic file in the bundled data."""
        try:
            data_dir = importlib.resources.files("smith.data")
        except Exception as exc:
            raise TemplateSourceError(
                f"Failed to locate bundled template data: {exc}"
            ) from exc

        if not hasattr(data_dir, "joinpath"):
            raise TemplateSourceError("Bundled template data directory not found")

        data_path = Path(str(data_dir.joinpath()))
        if not data_path.is_dir():
            raise TemplateSourceError(
                f"Bundled template data directory not found: {data_path}"
            )

        all_specs = _collect_specs_from_directory(data_path)
        specs = [s for s in all_specs if _is_agentic_path(s.relative_path)]

        if not specs:
            raise TemplateSourceError("Bundled template data contains no agentic files")

        return specs

    def gitignore_patterns(self) -> list[str]:
        """Return the standard gitignore patterns for bundled templates."""
        return list(GITIGNORE_PATTERNS)


class LocalTemplateSource:
    """Resolve templates from a local directory on disk."""

    def __init__(self, path: Path) -> None:
        """Initialise with the local template directory path."""
        self._path = path

    def resolve(self) -> list[FileSpec]:
        """Return FileSpec list for every file in the local directory."""
        if not self._path.is_dir():
            raise TemplateSourceError(f"Template directory not found: {self._path}")
        return _collect_specs_from_directory(self._path)

    def gitignore_patterns(self) -> list[str]:
        """Return gitignore patterns derived from the local directory contents."""
        patterns: list[str] = []
        for item in sorted(self._path.iterdir()):
            name = item.name
            if item.is_dir():
                patterns.append(f"{name}/")
            else:
                patterns.append(name)
        return patterns


class UrlTemplateSource:
    """Resolve templates from a remote tar.gz or zip archive."""

    def __init__(self, url: str) -> None:
        """Initialise with the URL of the template archive."""
        self._url = url

    def resolve(self) -> list[FileSpec]:
        """Download, extract, and return FileSpec list for agentic files."""
        try:
            response = requests.get(self._url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise TemplateSourceError(
                f"Failed to download template from {self._url}: {exc}"
            ) from exc

        tmp_dir = tempfile.mkdtemp(prefix="smith_url_")
        try:
            try:
                if self._url.endswith(".zip"):
                    self._extract_zip(response.content, tmp_dir)
                else:
                    self._extract_tar(response.content, tmp_dir)
            except (tarfile.TarError, zipfile.BadZipFile, OSError) as exc:
                raise TemplateSourceError(
                    f"Failed to extract template archive from {self._url}: {exc}"
                ) from exc

            all_specs = _collect_specs_from_directory(Path(tmp_dir))
        finally:
            import shutil

            shutil.rmtree(tmp_dir, ignore_errors=True)

        specs = [s for s in all_specs if _is_agentic_path(s.relative_path)]

        if not specs:
            raise TemplateSourceError(
                f"Template archive from {self._url} contains no agentic files"
            )

        return specs

    def gitignore_patterns(self) -> list[str]:
        """Return the standard gitignore patterns for URL-sourced templates."""
        return list(GITIGNORE_PATTERNS)

    @staticmethod
    def _extract_tar(content: bytes, target_dir: str) -> None:
        """Extract a tar.gz archive, stripping the top-level directory."""
        import io

        with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
            members = tar.getmembers()
            if not members:
                raise TemplateSourceError("Tar archive is empty")

            root_dir = members[0].name.split("/")[0]
            for member in members:
                member_path = Path(member.name)
                if member_path.parts[0] == root_dir:
                    member.name = str(Path(*member_path.parts[1:]))
                if member.name:
                    tar.extract(member, target_dir, filter="data")

    @staticmethod
    def _extract_zip(content: bytes, target_dir: str) -> None:
        """Extract a zip archive, stripping the top-level directory."""
        import io

        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = zf.namelist()
            if not names:
                raise TemplateSourceError("Zip archive is empty")

            root_dir = names[0].split("/")[0]
            for name in names:
                if name == root_dir + "/":
                    continue
                if name.startswith(root_dir + "/"):
                    zf.extract(name, target_dir)


class TemplateSourceAdapter:
    """Dispatch to the correct TemplateSourcePort implementation based on kind."""

    def __init__(self, source: TemplateSource) -> None:
        """Initialise with the TemplateSource value object."""
        self._source = source

    def resolve(self) -> list[FileSpec]:
        """Resolve template files via the appropriate source strategy."""
        if self._source.kind == "bundled":
            return BundledTemplateSource().resolve()
        if self._source.kind == "local":
            return LocalTemplateSource(Path(self._source.location)).resolve()
        if self._source.kind == "url":
            return UrlTemplateSource(self._source.location).resolve()
        raise TemplateSourceError(f"Unknown template source kind: {self._source.kind}")

    def gitignore_patterns(self) -> list[str]:
        """Return gitignore patterns via the appropriate source strategy."""
        if self._source.kind == "bundled":
            return BundledTemplateSource().gitignore_patterns()
        if self._source.kind == "local":
            return LocalTemplateSource(Path(self._source.location)).gitignore_patterns()
        if self._source.kind == "url":
            return UrlTemplateSource(self._source.location).gitignore_patterns()
        raise TemplateSourceError(f"Unknown template source kind: {self._source.kind}")
