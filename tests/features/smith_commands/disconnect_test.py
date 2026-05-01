"""Rule: Disconnect from a project.

BDD scenarios for smith disconnect removing managed files while preserving
user-tracked files and the '# smith managed' section.
"""

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import FileSpec, TemplateSource
from tests.features.smith_commands.conftest import (
    DEFAULT_SPECS,
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


def test_smith_commands_cd5ba959(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with all agentic files present and a
        `# smith managed` section in .gitignore
    When the engineer runs `smith disconnect`
    Then all agentic files that are gitignored by `# smith managed` are removed
        from the project directory
    And the `# smith managed` section is preserved in .gitignore
    And files not gitignored by `# smith managed` are not removed
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

    removed = connection.disconnect()

    assert Path("AGENTS.md") in removed
    assert Path(".opencode/agents/po.md") in removed
    assert Path(".templates/docs/ADR.template") in removed
    assert Path(".flowr/flows/main.yaml") in removed
    assert gitignore.has_section()
    patterns = gitignore.get_patterns()
    assert "AGENTS.md" in patterns
    assert ".opencode/" in patterns


def test_smith_commands_9411ceb4(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no `# smith managed`
        section in .gitignore
    When the engineer runs `smith disconnect`
    Then smith exits with code 0
    And no files are modified
    """
    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    removed = connection.disconnect()

    assert removed == []
    assert not gitignore.has_section()


def test_smith_commands_b755bfae(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where .opencode/ exists and is gitignored by
        `# smith managed` but .flowr/ is missing
    When the engineer runs `smith disconnect`
    Then .opencode/ is removed
    And no error is raised for the missing .flowr/
    And the `# smith managed` section is preserved in .gitignore
    """
    fs.write_atomic(
        [
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

    removed = connection.disconnect()

    assert Path(".opencode/agents/po.md") in removed
    assert Path(".flowr/flows/main.yaml") not in removed
    assert gitignore.has_section()


def test_smith_commands_8f2a9018(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where AGENTS.md is NOT gitignored by
        `# smith managed` (user tracks it) but .opencode/ IS gitignored by
        `# smith managed`
    When the engineer runs `smith disconnect`
    Then .opencode/ is removed
    And AGENTS.md is not removed (it is not in the smith-managed section)
    And the `# smith managed` section is preserved in .gitignore
    """
    user_content = b"# user's agents\n"
    fs.write_atomic(
        [
            FileSpec(relative_path=Path("AGENTS.md"), content=user_content),
            FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# PO\n"),
        ]
    )
    gitignore.add_section([".opencode/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    removed = connection.disconnect()

    assert Path(".opencode/agents/po.md") in removed
    assert Path("AGENTS.md") not in removed
    assert fs.read(Path("AGENTS.md")) == user_content
    assert gitignore.has_section()
