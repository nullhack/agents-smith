from pathlib import Path

import pytest

from smith.domain.value_objects import (
    FileSpec,
    TemplateSource,
)


class InMemoryFileSystem:
    def __init__(self) -> None:
        self._files: dict[Path, bytes] = {}

    def check_conflicts(self, paths: list[Path]) -> list[Path]:
        return [p for p in paths if p in self._files]

    def write_atomic(self, specs: list[FileSpec]) -> None:
        for spec in specs:
            self._files[spec.relative_path] = spec.content

    def remove(self, paths: list[Path]) -> None:
        for p in paths:
            self._files.pop(p, None)

    def exists(self, paths: list[Path]) -> dict[Path, bool]:
        return {p: p in self._files for p in paths}

    def written_paths(self) -> set[Path]:
        return set(self._files.keys())

    def read(self, path: Path) -> bytes | None:
        return self._files.get(path)


class InMemoryGitignore:
    def __init__(self) -> None:
        self._patterns: list[str] = []
        self._has_section: bool = False
        self._source: TemplateSource | None = None
        self._pre_existing_lines: list[str] = []

    def set_pre_existing_lines(self, lines: list[str]) -> None:
        self._pre_existing_lines = lines

    def get_all_lines(self) -> list[str]:
        lines = list(self._pre_existing_lines)
        if self._has_section:
            header = (
                f"# smith managed source:{self._source.location}"
                if self._source
                else "# smith managed"
            )
            lines.extend([header])
            lines.extend(self._patterns)
            lines.append("# end smith managed")
        return lines

    def add_section(self, patterns: list[str]) -> None:
        self._patterns = list(patterns)
        self._has_section = True

    def has_section(self) -> bool:
        return self._has_section

    def get_patterns(self) -> list[str]:
        return list(self._patterns)

    def save_source(self, source: TemplateSource) -> None:
        self._source = source

    def load_source(self) -> TemplateSource | None:
        return self._source


class StubTemplateSource:
    def __init__(
        self,
        specs: list[FileSpec] | None = None,
        patterns: list[str] | None = None,
    ) -> None:
        self._specs = specs or []
        self._patterns = patterns or [
            "AGENTS.md",
            ".opencode/",
            ".templates/",
            ".flowr/",
        ]

    def resolve(self) -> list[FileSpec]:
        return list(self._specs)

    def gitignore_patterns(self) -> list[str]:
        return list(self._patterns)


DEFAULT_SPECS = [
    FileSpec(relative_path=Path("AGENTS.md"), content=b"# Agents configuration\n"),
    FileSpec(
        relative_path=Path(".opencode/agents/po.md"),
        content=b"# Product Owner agent\n",
    ),
    FileSpec(
        relative_path=Path(".templates/docs/ADR.template"),
        content=b"# ADR template\n",
    ),
    FileSpec(
        relative_path=Path(".flowr/flows/main.yaml"),
        content=b"# Main flow\n",
    ),
]


@pytest.fixture
def default_template() -> StubTemplateSource:
    return StubTemplateSource(
        specs=DEFAULT_SPECS,
        patterns=["AGENTS.md", ".opencode/", ".templates/", ".flowr/"],
    )


@pytest.fixture
def fs() -> InMemoryFileSystem:
    return InMemoryFileSystem()


@pytest.fixture
def gitignore() -> InMemoryGitignore:
    return InMemoryGitignore()


@pytest.fixture
def metadata(gitignore: InMemoryGitignore) -> InMemoryGitignore:
    return gitignore
