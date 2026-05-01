"""Connect use-case — wire a project to a template source."""

from __future__ import annotations

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import TemplateSource
from smith.infrastructure.filesystem import AtomicFileSystem
from smith.infrastructure.gitignore import GitignoreManager
from smith.infrastructure.metadata import SectionMetadata
from smith.infrastructure.template_source import TemplateSourceAdapter


class ConnectUseCase:
    """Orchestrate the connection of a project to a template source."""

    def __init__(self, project_dir: Path) -> None:
        """Initialise with the target project directory."""
        self._project_dir = project_dir

    def execute(self, source: TemplateSource, overwrite: bool = False) -> None:
        """Connect the project to the given template source."""
        connection = Connection(
            template_source_port=TemplateSourceAdapter(source),
            filesystem_port=AtomicFileSystem(self._project_dir),
            gitignore_port=GitignoreManager(self._project_dir),
            metadata_port=SectionMetadata(self._project_dir),
        )
        connection.connect(source=source, overwrite=overwrite)
