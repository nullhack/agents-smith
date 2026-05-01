from smith.domain.connection import Connection
from tests.features.smith_commands.conftest import (
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


def test_disconnect_with_empty_patterns_returns_empty_list():
    gitignore = InMemoryGitignore()
    gitignore.add_section([])
    fs = InMemoryFileSystem()
    metadata = gitignore
    default_template = StubTemplateSource()

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    removed = connection.disconnect()

    assert removed == []
    assert gitignore.has_section()
