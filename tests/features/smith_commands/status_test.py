"""Rule: Check connection status.

BDD scenarios for smith status reporting connection state, present/missing
files, and template source information.
"""

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import (
    ConnectionState,
    FileSpec,
    TemplateSource,
)
from tests.features.smith_commands.conftest import (
    DEFAULT_SPECS,
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


def test_smith_commands_447e3cbf(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with all agentic files present and a
        `# smith managed` section in .gitignore
    When the engineer runs `smith status`
    Then smith reports "Connected" with a list of present agentic files
    """
    for spec in DEFAULT_SPECS:
        fs.write_atomic([spec])
    gitignore.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    status = connection.status()

    assert status.state == ConnectionState.CONNECTED
    assert len(status.present_files) == len(DEFAULT_SPECS)
    assert len(status.missing_files) == 0
    assert status.source == TemplateSource(kind="bundled", location="agents-smith")


def test_smith_commands_3f364b1d(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where .opencode/ and AGENTS.md exist but
        .templates/ and .flowr/ are missing
    When the engineer runs `smith status`
    Then smith reports "Partial" with a list of present and missing agentic files
    And suggests `smith connect --overwrite` or `smith disconnect`
    """
    fs.write_atomic(
        [
            FileSpec(relative_path=Path("AGENTS.md"), content=b"# Agents\n"),
            FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# PO\n"),
        ]
    )
    gitignore.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    status = connection.status()

    assert status.state == ConnectionState.PARTIAL
    assert Path("AGENTS.md") in status.present_files
    assert Path(".opencode/agents/po.md") in status.present_files
    assert Path(".templates/docs/ADR.template") in status.missing_files
    assert Path(".flowr/flows/main.yaml") in status.missing_files


def test_smith_commands_76e27d0a(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files but a `# smith managed`
        section in .gitignore
    When the engineer runs `smith status`
    Then smith reports "Disconnected"
    And suggests `smith connect` to reconnect
    """
    gitignore.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    status = connection.status()

    assert status.state == ConnectionState.DISCONNECTED
    assert len(status.present_files) == 0
    assert len(status.missing_files) == len(DEFAULT_SPECS)


def test_smith_commands_94ebcd86(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no `# smith managed`
        section in .gitignore
    When the engineer runs `smith status`
    Then smith reports "Not connected"
    And suggests `smith connect` to get started
    """
    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    status = connection.status()

    assert status.state == ConnectionState.DISCONNECTED
    assert len(status.present_files) == 0
    assert len(status.missing_files) == len(DEFAULT_SPECS)


def test_smith_commands_10843402(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a connected project directory
    When the engineer runs `smith status --json`
    Then smith outputs machine-readable JSON with connection status,
        present files list, and template source
    """
    for spec in DEFAULT_SPECS:
        fs.write_atomic([spec])
    gitignore.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    status = connection.status()

    json_output = status.to_dict()

    assert json_output["state"] == "connected"
    assert isinstance(json_output["present_files"], list)
    assert isinstance(json_output["missing_files"], list)
    assert json_output["source"]["kind"] == "bundled"
    assert json_output["source"]["location"] == "agents-smith"
