"""Atomic file-system adapter — write files transactionally or remove them."""

import shutil
import tempfile
from pathlib import Path

from smith.domain.value_objects import FileSpec


class FileSystemError(Exception):
    """Raised when an atomic file operation fails."""


class AtomicFileSystem:
    """File-system adapter that writes files atomically via a staging directory."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the project root directory."""
        self._project_dir = project_dir

    def check_conflicts(self, paths: list[Path]) -> list[Path]:
        """Return the subset of *paths* that already exist on disk."""
        return [p for p in paths if (self._project_dir / p).exists()]

    def write_atomic(self, specs: list[FileSpec]) -> None:
        """Write all specs atomically; roll back on failure."""
        if not specs:
            return
        staging = Path(tempfile.mkdtemp(dir=self._project_dir))
        try:
            for spec in specs:
                dest = staging / spec.relative_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(spec.content)
            for spec in specs:
                final = self._project_dir / spec.relative_path
                final.parent.mkdir(parents=True, exist_ok=True)
                Path(staging / spec.relative_path).replace(final)
        except Exception as err:
            shutil.rmtree(staging, ignore_errors=True)
            raise FileSystemError("Atomic write failed") from err
        else:
            shutil.rmtree(staging, ignore_errors=True)

    def remove(self, paths: list[Path]) -> None:
        """Remove the given paths from the project directory."""
        for p in paths:
            full = self._project_dir / p
            if full.exists():
                full.unlink()

    def exists(self, paths: list[Path]) -> dict[Path, bool]:
        """Return a mapping of each path to whether it exists on disk."""
        return {p: (self._project_dir / p).exists() for p in paths}
