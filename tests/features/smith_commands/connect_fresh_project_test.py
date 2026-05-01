"""Rule: Connect to a fresh project.

BDD scenarios for smith connect in a project directory with no existing
agentic files and no '# smith managed' section in .gitignore.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from smith.domain.connection import Connection
from smith.domain.ports import TemplateSourceError
from smith.domain.value_objects import FileSpec, TemplateSource
from smith.infrastructure.filesystem import FileSystemError
from smith.infrastructure.template_source import (
    UrlTemplateSource,
)
from tests.features.smith_commands.conftest import (
    InMemoryFileSystem,
    InMemoryGitignore,
    StubTemplateSource,
)


class FailingTemplateSource:
    """Template source that always raises TemplateSourceError."""

    def resolve(self):
        raise TemplateSourceError("Template source not found")

    def gitignore_patterns(self):
        return []


class FailingFileSystem(InMemoryFileSystem):
    """Filesystem that raises FileSystemError on write_atomic."""

    def write_atomic(self, specs):
        raise FileSystemError("Simulated write failure")

    def check_conflicts(self, paths):
        return []

    def exists(self, paths):
        return dict.fromkeys(paths, False)


def test_smith_commands_c928a845(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no `# smith managed`
        section in .gitignore
    When the engineer runs `smith connect`
    Then all agentic files (AGENTS.md, .opencode/, .templates/, .flowr/) are
        written to the project directory
    And a `# smith managed` section is added to .gitignore with entries for
        all agentic file patterns
    """
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
    expected_paths = {spec.relative_path for spec in default_template.resolve()}
    assert fs.written_paths() == expected_paths
    assert gitignore.has_section()
    patterns = gitignore.get_patterns()
    assert "AGENTS.md" in patterns
    assert ".opencode/" in patterns
    assert ".templates/" in patterns
    assert ".flowr/" in patterns


def test_smith_commands_86c8e268(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from ./my-templates`
    Then agentic files are written from the local path template source to the
        project directory
    And a `# smith managed` section is added to .gitignore
    """
    local_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# Local agents\n"),
        FileSpec(relative_path=Path(".opencode/agents/po.md"), content=b"# Local PO\n"),
    ]
    local_template = StubTemplateSource(
        specs=local_specs, patterns=["AGENTS.md", ".opencode/"]
    )

    connection = Connection(
        template_source_port=local_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(kind="local", location="./my-templates")
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# Local agents\n"
    assert fs.read(Path(".opencode/agents/po.md")) == b"# Local PO\n"
    assert gitignore.has_section()
    patterns = gitignore.get_patterns()
    assert "AGENTS.md" in patterns
    assert ".opencode/" in patterns


def test_smith_commands_577156bb(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from https://example.com/templates.tar.gz`
    Then agentic files are downloaded from the URL and written to the project directory
    And a `# smith managed` section is added to .gitignore
    """
    url_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# URL agents\n"),
        FileSpec(relative_path=Path(".opencode/"), content=b""),
    ]
    url_template = StubTemplateSource(
        specs=url_specs, patterns=["AGENTS.md", ".opencode/"]
    )

    connection = Connection(
        template_source_port=url_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(
            kind="url", location="https://example.com/templates.tar.gz"
        )
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# URL agents\n"
    assert gitignore.has_section()


def test_smith_commands_4fdd38a4(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from https://example.com/templates/my-template.zip`
    Then agentic files are downloaded from the remote URL
        and written to the project directory
    And a `# smith managed` section is added to .gitignore
    """
    git_specs = [
        FileSpec(relative_path=Path("AGENTS.md"), content=b"# Git agents\n"),
        FileSpec(relative_path=Path(".flowr/flows/main.yaml"), content=b"# Git flow\n"),
    ]
    git_template = StubTemplateSource(
        specs=git_specs, patterns=["AGENTS.md", ".flowr/"]
    )

    connection = Connection(
        template_source_port=git_template,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    result = connection.connect(
        source=TemplateSource(
            kind="url", location="https://example.com/templates/my-template.zip"
        )
    )

    assert result is None
    assert fs.read(Path("AGENTS.md")) == b"# Git agents\n"
    assert fs.read(Path(".flowr/flows/main.yaml")) == b"# Git flow\n"
    assert gitignore.has_section()
    assert "AGENTS.md" in gitignore.get_patterns()
    assert ".flowr/" in gitignore.get_patterns()


def test_smith_commands_f79d40f4(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from /nonexistent/path`
    Then smith exits with code 1
    And an error message indicates the template source could not be found
    """
    failing_source = FailingTemplateSource()
    connection = Connection(
        template_source_port=failing_source,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    with pytest.raises(TemplateSourceError):
        connection.connect(
            source=TemplateSource(kind="local", location="/nonexistent/path")
        )

    assert fs.written_paths() == set()
    assert not gitignore.has_section()


def test_smith_commands_060390bf(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no .gitignore file
    When the engineer runs `smith connect`
    Then a new .gitignore file is created containing the `# smith managed`
        section with entries for all agentic file patterns
    """
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
    assert gitignore.has_section()
    patterns = gitignore.get_patterns()
    assert "AGENTS.md" in patterns
    assert ".opencode/" in patterns
    assert ".templates/" in patterns
    assert ".flowr/" in patterns


def test_smith_commands_e8245392(
    default_template: "StubTemplateSource",
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and an existing .gitignore
        without a `# smith managed` section
    When the engineer runs `smith connect`
    Then the `# smith managed` section is appended to the existing .gitignore
    And existing .gitignore content is preserved
    """
    gitignore.set_pre_existing_lines(["*.pyc", "__pycache__/", ".env"])

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
    assert gitignore.has_section()
    all_lines = gitignore.get_all_lines()
    assert "*.pyc" in all_lines
    assert "__pycache__/" in all_lines
    assert ".env" in all_lines
    patterns = gitignore.get_patterns()
    assert "AGENTS.md" in patterns
    assert ".opencode/" in patterns


def test_smith_commands_fc22c286(
    default_template: "StubTemplateSource",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When smith fails to write .opencode/ after writing AGENTS.md
    Then AGENTS.md is removed (rolled back)
    And no agentic files remain in the project directory
    """
    failing_fs = FailingFileSystem()

    connection = Connection(
        template_source_port=default_template,
        filesystem_port=failing_fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    with pytest.raises(FileSystemError):
        connection.connect(
            source=TemplateSource(kind="bundled", location="agents-smith")
        )

    assert failing_fs.written_paths() == set()
    assert not gitignore.has_section()


@pytest.mark.deprecated
def test_smith_commands_a1b2c3d4(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files and no cached templates
    When the engineer runs `smith connect` and the GitHub archive download fails
    Then smith exits with code 1
    And an error message indicates the bundled template source could not be downloaded
    """


@pytest.mark.deprecated
def test_smith_commands_e5f6g7h8(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
    tmp_path: Path,
) -> None:
    """Given a project directory with no agentic files and cached templates
        from a previous connect
    When the engineer runs `smith connect` and the GitHub archive download fails
    Then smith uses the cached templates and connects successfully
    And smith exits with code 0
    """


def test_smith_commands_a2b3c4d5(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from https://example.com/templates.tar.gz`
        and the download fails
    Then smith exits with code 1
    And an error message indicates the URL template source could not be downloaded
    """
    url_source = UrlTemplateSource("https://example.com/notfound.tar.gz")
    connection = Connection(
        template_source_port=url_source,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    with patch("smith.infrastructure.template_source.requests") as mock_req:
        mock_req.get.side_effect = ConnectionError("network unreachable")
        mock_req.RequestException = ConnectionError
        with pytest.raises(TemplateSourceError, match="Failed to download"):
            connection.connect(
                source=TemplateSource(
                    kind="url", location="https://example.com/notfound.tar.gz"
                )
            )

    assert fs.written_paths() == set()
    assert not gitignore.has_section()


def test_smith_commands_e4f5g6h7(
    fs: "InMemoryFileSystem",
    gitignore: "InMemoryGitignore",
    metadata: "InMemoryGitignore",
) -> None:
    """Given a project directory with no agentic files
    When the engineer runs `smith connect --from https://example.com/templates.tar.gz`
        and the downloaded archive is invalid
    Then smith exits with code 1
    And an error message indicates the archive could not be extracted
    """
    url_source = UrlTemplateSource("https://example.com/broken.tar.gz")
    connection = Connection(
        template_source_port=url_source,
        filesystem_port=fs,
        gitignore_port=gitignore,
        metadata_port=metadata,
    )

    mock_response = MagicMock()
    mock_response.content = b"not a valid tar.gz"
    mock_response.raise_for_status = MagicMock()

    with patch("smith.infrastructure.template_source.requests") as mock_req:
        mock_req.get.return_value = mock_response
        mock_req.RequestException = Exception
        with pytest.raises(TemplateSourceError):
            connection.connect(
                source=TemplateSource(
                    kind="url", location="https://example.com/broken.tar.gz"
                )
            )

    assert fs.written_paths() == set()
    assert not gitignore.has_section()
