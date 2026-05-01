"""Domain value objects — immutable data structures used across the domain."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class FileSpec:
    """A template file's relative path and binary content."""

    relative_path: Path
    content: bytes


@dataclass(frozen=True)
class TemplateSource:
    """Identifies where a template originates (bundled, local, or URL)."""

    kind: Literal["bundled", "local", "url"]
    location: str


class ConnectionState(Enum):
    """Possible states of a project's connection to a template source."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PARTIAL = "partial"


@dataclass(frozen=True)
class ConnectionStatus:
    """Snapshot of a project's connection state and file presence."""

    state: ConnectionState
    source: TemplateSource | None
    present_files: list[Path]
    missing_files: list[Path]

    def to_dict(self) -> dict:
        """Serialise the status to a plain dictionary."""
        return {
            "state": self.state.value,
            "source": (
                {"kind": self.source.kind, "location": self.source.location}
                if self.source
                else None
            ),
            "present_files": [str(p) for p in self.present_files],
            "missing_files": [str(p) for p in self.missing_files],
        }


@dataclass(frozen=True)
class GitignoreSection:
    """A delimited block of patterns inside .gitignore managed by smith."""

    patterns: list[str]
    start_marker: str = "# smith managed"
    end_marker: str = "# end smith managed"
