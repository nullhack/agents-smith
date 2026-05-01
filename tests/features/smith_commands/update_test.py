"""Rule: Update agentic files.

BDD scenarios for smith update refreshing connected projects from the
template source, including auto-connect for not-connected projects.
"""

from pathlib import Path

import pytest

from smith.domain.connection import Connection
from smith.domain.ports import TemplateSourceError
from smith.domain.value_objects import FileSpec, TemplateSource
from tests.features.smith_commands.conftest import (
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


def test_smith_commands_e4d06612(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with all agentic files present and a
        `# smith managed` section in .gitignore
    When the engineer runs `smith update`
    Then all agentic files that are in the `# smith managed` section are
        overwritten with the latest template versions
    And files not managed by smith are not touched
    And smith exits with code 0
    """
    old_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# old agents\n"),
        FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# old po\n"),
    ]
    fs.write_atomic(old_specs)
    gitignore.add_section(["AGENTS.md", ".opencode/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.update()

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# Agents configuration\n"
    assert fs.read(Path(".opencode/agents/po.md")) == b"# Product Owner agent\n"


def test_smith_commands_d348166e(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with all agentic files present and a
        `# smith managed` section in .gitignore
    When the engineer runs `smith update --from ./new-templates`
    Then all managed agentic files are overwritten with files from the new
        template source
    And smith exits with code 0
    """
    new_template = StubTemplateSource(
        specs=[
            FileSpec(relative_path=Path("AGENTS.md"), content=b"# New agents\n"),
            FileSpec(
                relative_path=Path(".opencode/agents/po.md"), content=b"# New PO\n"
            ),
        ],
        patterns=["AGENTS.md", ".opencode/"],
    )
    old_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# old agents\n"),
        FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# old po\n"),
    ]
    fs.write_atomic(old_specs)
    gitignore.add_section(["AGENTS.md", ".opencode/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=new_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.update(
        source=TemplateSource(kind="local", location="./new-templates")
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# New agents\n"
    assert fs.read(Path(".opencode/agents/po.md")) == b"# New PO\n"


def test_smith_commands_9a01f4e2(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no `# smith managed`
        section in .gitignore
    When the engineer runs `smith update`
    Then smith behaves as `smith connect` — all agentic files are written
        and a `# smith managed` section is added to .gitignore
    And smith exits with code 0
    """
    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.update()

    assert result is None
    expected_paths = {spec.relative_path for spec in default_template.resolve()}
    assert fs.written_paths() == expected_paths
    assert gitignore.has_section()


def test_smith_commands_7af2f4d1(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a connected project directory
    When the engineer runs `smith update --from /nonexistent/path`
    Then smith exits with code 1
    And an error message indicates the template source could not be found
    """

    class FailingTemplateSource:
        def resolve(self):
            raise TemplateSourceError("Template source not found")

        def gitignore_patterns(self):
            return ["AGENTS.md"]

    gitignore.add_section(["AGENTS.md", ".opencode/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=FailingTemplateSource(),
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    with pytest.raises(TemplateSourceError):
        connection.update(
            source=TemplateSource(kind="local", location="/nonexistent/path")
        )
