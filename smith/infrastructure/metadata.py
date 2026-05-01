"""Metadata adapter — persist and load template source info in .gitignore."""

from pathlib import Path

from smith.domain.value_objects import TemplateSource
from smith.infrastructure.gitignore import START_MARKER, GitignoreManager


class SectionMetadata:
    """Store and retrieve template source metadata inside the gitignore section."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the project root directory."""
        self._gitignore = GitignoreManager(project_dir)

    def save_source(self, source: TemplateSource) -> None:
        """Write the source identifier into the smith-managed section header."""
        lines = self._gitignore._read_lines()
        bounds = self._gitignore._find_section_bounds(lines)
        if bounds is None:
            return
        start = bounds[0]
        header = f"{START_MARKER} source:{source.kind}:{source.location}\n"
        lines[start] = header
        self._gitignore._write_lines(lines)

    def load_source(self) -> TemplateSource | None:
        """Read the source identifier from the smith-managed section header."""
        lines = self._gitignore._read_lines()
        bounds = self._gitignore._find_section_bounds(lines)
        if bounds is None:
            return None
        header = lines[bounds[0]].strip()
        for part in header.split():
            if part.startswith("source:"):
                value = part[len("source:") :]
                if ":" in value:
                    kind, location = value.split(":", 1)
                    return TemplateSource(kind=kind, location=location)  # type: ignore[arg-type]
        return None
