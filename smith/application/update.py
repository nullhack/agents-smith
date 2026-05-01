"""Update use-case — refresh agentic files in a connected project."""

from __future__ import annotations

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import TemplateSource
from smith.infrastructure.filesystem import AtomicFileSystem
from smith.infrastructure.gitignore import GitignoreManager
from smith.infrastructure.metadata import SectionMetadata
from smith.infrastructure.template_source import TemplateSourceAdapter


class UpdateUseCase:
    """Orchestrate updating agentic files in an already-connected project."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the target project directory."""
        self._project_dir = project_dir

    def execute(self, source: TemplateSource | None = None) -> None:
        """Update the project's agentic files, optionally from a new source."""
        connection = Connection(
            template_source_port=TemplateSourceAdapter(
                source or TemplateSource(kind="bundled", location="agents-smith"),
            ),
            filesystem_port=AtomicFileSystem(self._project_dir),
            gitignore_port=GitignoreManager(self._project_dir),
            metadata_port=SectionMetadata(self._project_dir),
        )
        connection.update(source=source)
