"""Manage the smith-managed section in .gitignore."""

from pathlib import Path

START_MARKER = "# smith managed"
END_MARKER = "# end smith managed"


class GitignoreManager:
    """Read and mutate the smith-managed section of a project's .gitignore."""

    def __init__(self, project_dir: Path) -> None:
        self._path = project_dir / ".gitignore"

    def add_section(self, patterns: list[str]) -> None:
        """Add or replace the smith-managed section in .gitignore."""
        lines = self._read_lines()
        bounds = self._find_section_bounds(lines)
        section_lines = [f"{START_MARKER}\n"]
        for p in patterns:
            section_lines.append(f"{p}\n")
        section_lines.append(f"{END_MARKER}\n")
        if bounds is not None:
            start, end = bounds
            lines[start : end + 1] = section_lines
        else:
            if lines and lines[-1].strip():
                lines.append("\n")
            lines.extend(section_lines)
        self._write_lines(lines)

    def has_section(self) -> bool:
        """Return whether a smith-managed section exists in .gitignore."""
        lines = self._read_lines()
        return self._find_section_bounds(lines) is not None

    def get_patterns(self) -> list[str]:
        """Return the non-comment patterns inside the smith-managed section."""
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
        if not self._path.exists():
            return []
        return self._path.read_text().splitlines(keepends=True)

    def _write_lines(self, lines: list[str]) -> None:
        content = "".join(lines)
        if content and not content.endswith("\n"):
            content += "\n"
        self._path.write_text(content)

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
