"""Port definitions — interfaces that infrastructure adapters must implement."""

from pathlib import Path
from typing import Protocol

from smith.domain.value_objects import (
    FileSpec,
    TemplateSource,
)


class TemplateSourceError(Exception):
    """Raised when a template source cannot be resolved."""


class TemplateSourcePort(Protocol):
    """Interface for resolving template file specifications."""

    def resolve(self) -> list[FileSpec]:
        """Return the list of file specs from this template source."""
        ...

    def gitignore_patterns(self) -> list[str]:
        """Return the gitignore patterns for this template source."""
        ...


class FileSystemPort(Protocol):
    """Interface for atomic file-system operations."""

    def check_conflicts(self, paths: list[Path]) -> list[Path]:
        """Return the subset of *paths* that already exist on disk."""
        ...

    def write_atomic(self, specs: list[FileSpec]) -> None:
        """Write all specs atomically; roll back on failure."""
        ...

    def remove(self, paths: list[Path]) -> None:
        """Remove the given paths from the project directory."""
        ...

    def exists(self, paths: list[Path]) -> dict[Path, bool]:
        """Return a mapping of each path to whether it exists on disk."""
        ...


class GitignorePort(Protocol):
    """Interface for managing the smith-managed .gitignore section."""

    def add_section(self, patterns: list[str]) -> None:
        """Add or replace the smith-managed section in .gitignore."""
        ...

    def has_section(self) -> bool:
        """Return whether a smith-managed section exists in .gitignore."""
        ...

    def get_patterns(self) -> list[str]:
        """Return the patterns listed inside the smith-managed section."""
        ...


class MetadataPort(Protocol):
    """Interface for persisting and loading template source metadata."""

    def save_source(self, source: TemplateSource) -> None:
        """Write the source identifier into the smith-managed section header."""
        ...

    def load_source(self) -> TemplateSource | None:
        """Read the source identifier from the smith-managed section header."""
        ...
