"""Connection aggregate — core domain logic for connect/disconnect/update/status."""

from pathlib import Path

from smith.domain.ports import (
    FileSystemPort,
    GitignorePort,
    MetadataPort,
    TemplateSourcePort,
)
from smith.domain.value_objects import (
    ConnectionState,
    ConnectionStatus,
    FileSpec,
    TemplateSource,
)


class Connection:
    """Domain aggregate that manages the lifecycle of agentic file connections."""

    def __init__(
        self,
        template_source_port: TemplateSourcePort,
        filesystem_port: FileSystemPort,
        gitignore_port: GitignorePort,
        metadata_port: MetadataPort,
    ) -> None:
        """Initialise the Connection with its required ports."""
        self._template_source_port = template_source_port
        self._filesystem_port = filesystem_port
        self._gitignore_port = gitignore_port
        self._metadata_port = metadata_port

    def connect(
        self,
        source: TemplateSource,
        overwrite: bool = False,
    ) -> None:
        """Write agentic files and register the connection in .gitignore."""
        specs = self._template_source_port.resolve()
        paths = [spec.relative_path for spec in specs]

        specs = self._resolve_specs(specs, paths, overwrite)
        self._commit(specs, source)

    def _commit(self, specs: list[FileSpec], source: TemplateSource) -> None:
        self._filesystem_port.write_atomic(specs)
        self._gitignore_port.add_section(
            self._template_source_port.gitignore_patterns()
        )
        self._metadata_port.save_source(source)

    def _resolve_specs(
        self,
        specs: list[FileSpec],
        paths: list[Path],
        overwrite: bool = False,
    ) -> list[FileSpec]:
        conflicting = self._filesystem_port.check_conflicts(paths)
        if not conflicting:
            return specs

        unmanaged_existing = {
            p
            for p in conflicting
            if not self._is_path_managed(p, self._gitignore_port.get_patterns())
        }

        if overwrite:
            return [s for s in specs if s.relative_path not in unmanaged_existing]

        if not unmanaged_existing:
            return specs
        return [s for s in specs if s.relative_path not in unmanaged_existing]

    @staticmethod
    def _is_path_managed(path: Path, managed_patterns: list[str]) -> bool:
        path_str = str(path)
        return any(
            path_str == pattern or path_str.startswith(pattern)
            for pattern in managed_patterns
        )

    def disconnect(self) -> list[Path]:
        """Remove agentic files and the .gitignore section; return removed paths."""
        if not self._gitignore_port.has_section():
            return []

        managed_patterns = self._gitignore_port.get_patterns()
        if not managed_patterns:
            return []

        all_template_specs = self._template_source_port.resolve()
        all_template_paths = [spec.relative_path for spec in all_template_specs]

        managed_paths = [
            p for p in all_template_paths if self._is_path_managed(p, managed_patterns)
        ]

        existence = self._filesystem_port.exists(managed_paths)
        paths_to_remove = [p for p in managed_paths if existence.get(p, False)]

        self._filesystem_port.remove(paths_to_remove)
        return paths_to_remove

    def update(
        self,
        source: TemplateSource | None = None,
    ) -> None:
        """Refresh agentic files, optionally from a new template source."""
        if not self._gitignore_port.has_section():
            fallback_source = source or TemplateSource(
                kind="bundled", location="agents-smith"
            )
            return self.connect(source=fallback_source)

        resolved_source = (
            source
            or self._metadata_port.load_source()
            or TemplateSource(kind="bundled", location="agents-smith")
        )

        specs = self._template_source_port.resolve()
        paths = [spec.relative_path for spec in specs]

        specs = self._resolve_specs(specs, paths)

        self._commit(specs, resolved_source)
        return None

    def status(self) -> ConnectionStatus:
        """Return the current connection status of the project."""
        source = self._metadata_port.load_source()
        all_specs = self._template_source_port.resolve()
        all_paths = [spec.relative_path for spec in all_specs]
        existence = self._filesystem_port.exists(all_paths)
        present_files = [p for p in all_paths if existence.get(p, False)]
        missing_files = [p for p in all_paths if not existence.get(p, False)]

        if not self._gitignore_port.has_section() or not present_files:
            state = ConnectionState.DISCONNECTED
        elif missing_files:
            state = ConnectionState.PARTIAL
        else:
            state = ConnectionState.CONNECTED

        return ConnectionStatus(
            state=state,
            source=source,
            present_files=present_files,
            missing_files=missing_files,
        )
