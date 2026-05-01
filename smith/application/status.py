"""Status use-case — report the current connection state of a project."""

from __future__ import annotations

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import ConnectionStatus, TemplateSource
from smith.infrastructure.filesystem import AtomicFileSystem
from smith.infrastructure.gitignore import GitignoreManager
from smith.infrastructure.metadata import SectionMetadata
from smith.infrastructure.template_source import TemplateSourceAdapter


class StatusUseCase:
    """Orchestrate querying the connection status of a project."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the target project directory."""
        self._project_dir = project_dir

    def execute(self) -> ConnectionStatus:
        """Return the current connection status of the project."""
        connection = Connection(
            template_source_port=TemplateSourceAdapter(
                TemplateSource(kind="bundled", location="agents-smith"),
            ),
            filesystem_port=AtomicFileSystem(self._project_dir),
            gitignore_port=GitignoreManager(self._project_dir),
            metadata_port=SectionMetadata(self._project_dir),
        )
        return connection.status()
