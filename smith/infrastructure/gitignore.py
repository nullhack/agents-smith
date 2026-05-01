"""Gitignore adapter — manage the smith-managed section in .gitignore."""

from pathlib import Path

from smith.domain.value_objects import GitignoreSection

START_MARKER = "# smith managed"
END_MARKER = "# end smith managed"


class GitignoreManager:
    """Read and mutate the smith-managed section of a project's .gitignore."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the project root directory."""
        self._gitignore = project_dir / ".gitignore"

    def add_section(self, patterns: list[str]) -> None:
        """Add or replace the smith-managed section in .gitignore."""
        section = GitignoreSection(patterns=patterns)
        lines = self._read_lines()
        if self._find_section_bounds(lines) is not None:
            self._replace_section(lines, section)
        else:
            self._append_section(lines, section)

    def has_section(self) -> bool:
        """Return whether a smith-managed section exists in .gitignore."""
        lines = self._read_lines()
        return self._find_section_bounds(lines) is not None

    def get_patterns(self) -> list[str]:
        """Return the patterns listed inside the smith-managed section."""
        lines = self._read_lines()
        bounds = self._find_section_bounds(lines)
        if bounds is None:
            return []
        start, end = bounds
        patterns = []
        for line in lines[start + 1 : end]:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                patterns.append(stripped)
        return patterns

    def _read_lines(self) -> list[str]:
        if not self._gitignore.exists():
            return []
        return self._gitignore.read_text().splitlines(keepends=True)

    def _write_lines(self, lines: list[str]) -> None:
        content = "".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"
        self._gitignore.write_text(content)

    def _find_section_bounds(self, lines: list[str]) -> tuple[int, int] | None:
        start = None
        for i, line in enumerate(lines):
            if line.strip().startswith(START_MARKER):
                start = i
                break
        if start is None:
            return None
        for i in range(start + 1, len(lines)):
            if lines[i].strip() == END_MARKER:
                return (start, i)
        return None

    def _replace_section(self, lines: list[str], section: GitignoreSection) -> None:
        bounds = self._find_section_bounds(lines)
        if bounds is None:
            self._append_section(lines, section)
            return
        start, end = bounds
        header = lines[start].rstrip("\n")
        source_match = [p for p in header.split() if p.startswith("source:")]
        source_part = f" {source_match[0]}" if source_match else ""
        new_section = [f"{START_MARKER}{source_part}\n"]
        for p in section.patterns:
            new_section.append(f"{p}\n")
        new_section.append(f"{END_MARKER}\n")
        lines[start : end + 1] = new_section
        self._write_lines(lines)

    def _append_section(self, lines: list[str], section: GitignoreSection) -> None:
        new_lines = [f"{START_MARKER}\n"]
        for p in section.patterns:
            new_lines.append(f"{p}\n")
        new_lines.append(f"{END_MARKER}\n")
        if lines and lines[-1].strip():
            new_lines.insert(0, "\n")
        lines.extend(new_lines)
        self._write_lines(lines)
