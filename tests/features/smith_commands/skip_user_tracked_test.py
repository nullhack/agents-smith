"""Rule: Auto-update on connected projects, skip user-tracked files on fresh projects.

BDD scenarios for smith connect auto-updating managed files and skipping
user-tracked files.
"""

from __future__ import annotations

from pathlib import Path

from smith.domain.connection import Connection
from smith.domain.value_objects import FileSpec, TemplateSource
from tests.features.smith_commands.conftest import (
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


def test_smith_commands_df0455a5(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where .opencode/ exists and is listed in the
        `# smith managed` section of .gitignore
    When the engineer runs `smith connect`
    Then .opencode/ is updated with the template version (auto-update)
    And all other agentic files are written
    And smith exits with code 0
    """
    old_content = b"# old content\n"
    fs.write_atomic(
        [FileSpec(relative_path=Path(".opencode/agents/po.md"), content=old_content)]
    )

    gitignore.add_section([".opencode/"])

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="bundled", location="agents-smith")
    )

    assert result is None
    new_content = fs.read(Path(".opencode/agents/po.md"))
    assert new_content != old_content
    assert new_content == b"# Product Owner agent\n"
    assert Path("AGENTS.md") in fs.written_paths()
    assert Path(".templates/docs/ADR.template") in fs.written_paths()
    assert Path(".flowr/flows/main.yaml") in fs.written_paths()


def test_smith_commands_21c05bbb(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where AGENTS.md exists but is NOT in the
        `# smith managed` section of .gitignore (the user tracks it manually)
    When the engineer runs `smith connect`
    Then AGENTS.md is not overwritten
    And the remaining agentic files (.opencode/, .templates/, .flowr/) are written
    And a `# smith managed` section is added to .gitignore
    """
    user_content = b"# user's agents config\n"
    fs.write_atomic([FileSpec(relative_path=Path("AGENTS.md"), content=user_content)])

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="bundled", location="agents-smith")
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == user_content
    assert Path(".opencode/agents/po.md") in fs.written_paths()
    assert Path(".templates/docs/ADR.template") in fs.written_paths()
    assert Path(".flowr/flows/main.yaml") in fs.written_paths()
    assert gitignore.has_section()


def test_smith_commands_2a5f83d0(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where .opencode/ exists and is listed in the
        `# smith managed` section of .gitignore
    When the engineer runs `smith connect --overwrite`
    Then .opencode/ is replaced with the template version
    And all agentic files are written
    And files not in the `# smith managed` section are not touched
    """
    old_content = b"# old content\n"
    fs.write_atomic(
        [FileSpec(relative_path=Path(".opencode/agents/po.md"), content=old_content)]
    )
    gitignore.add_section([".opencode/"])

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="bundled", location="agents-smith"),
        overwrite=True,
    )

    assert result is None
    new_content = fs.read(Path(".opencode/agents/po.md"))
    assert new_content != old_content
    assert new_content == b"# Product Owner agent\n"
    assert Path("AGENTS.md") in fs.written_paths()
    assert Path(".templates/docs/ADR.template") in fs.written_paths()
    assert Path(".flowr/flows/main.yaml") in fs.written_paths()


def test_smith_commands_3e206149(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with all agentic files present and a
        `# smith managed` section in .gitignore
    When the engineer runs `smith connect`
    Then smith behaves as `smith update` — all managed agentic files are
        overwritten with the template versions
    And smith exits with code 0
    """
    old_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# old agents\n"),
        FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# old po\n"),
        FileSpec(
            relative_path=Path(".templates/docs/ADR.template"),
            content=b"# old template\n",
        ),
        FileSpec(relative_path=Path(".flowr/flows/main.yaml"), content=b"# old flow\n"),
    ]
    fs.write_atomic(old_specs)
    gitignore.add_section(["AGENTS.md", ".opencode/", ".templates/", ".flowr/"])
    metadata.save_source(TemplateSource(kind="bundled", location="agents-smith"))

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="bundled", location="agents-smith")
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# Agents configuration\n"
    assert fs.read(Path(".opencode/agents/po.md")) == b"# Product Owner agent\n"
    assert fs.read(Path(".templates/docs/ADR.template")) == b"# ADR template\n"
    assert fs.read(Path(".flowr/flows/main.yaml")) == b"# Main flow\n"
    assert gitignore.has_section()


def test_smith_commands_7d22e1d6(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory where AGENTS.md is NOT in `# smith managed`
        (user-tracked) and .opencode/ IS in `# smith managed`
    When the engineer runs `smith connect --overwrite`
    Then .opencode/ is replaced with the template version
    And AGENTS.md is not touched (it is not in the smith-managed section)
    """
    user_content = b"# user's agents config\n"
    old_opencode = b"# old opencode\n"
    fs.write_atomic(
        [
            FileSpec(relative_path=Path("AGENTS.md"), content=user_content),
            FileSpec(
                relative_path=Path(".opencode/agents/po.md"), content=old_opencode
            ),
        ]
    )
    gitignore.add_section([".opencode/"])

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="bundled", location="agents-smith"),
        overwrite=True,
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == user_content
    assert fs.read(Path(".opencode/agents/po.md")) == b"# Product Owner agent\n"
    assert Path(".templates/docs/ADR.template") in fs.written_paths()
    assert Path(".flowr/flows/main.yaml") in fs.written_paths()
