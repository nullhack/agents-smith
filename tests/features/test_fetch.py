import io
import zipfile
from pathlib import Path

import pytest

from smith.core import _extract_zip, fetch


def test_fetch_local_directory(tmp_path: Path) -> None:
    """
    Given a local template directory containing AGENTS.md,
    .opencode/agents/default.md, and src/main.py
    When smith fetches from the local directory
    Then it returns file specs for AGENTS.md and .opencode/agents/default.md
    And it does NOT return src/main.py
    """
    template = tmp_path / "template"
    template.mkdir()
    (template / "AGENTS.md").write_text("# agents")
    opencode = template / ".opencode" / "agents"
    opencode.mkdir(parents=True)
    (opencode / "default.md").write_text("default")
    src = template / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')")

    specs = fetch(str(template))
    rel_paths = [str(s.relative_path) for s in specs]

    assert any("AGENTS.md" in p for p in rel_paths)
    assert any(".opencode" in p for p in rel_paths)
    assert not any("src" in p for p in rel_paths)


def test_fetch_local_missing() -> None:
    """
    Given a nonexistent path "/nonexistent/path"
    When smith fetches from that path
    Then it raises RuntimeError with "not found"
    """
    with pytest.raises(RuntimeError, match="not found"):
        fetch("/nonexistent/path")


def test_fetch_local_no_matching(tmp_path: Path) -> None:
    """
    Given a local directory containing only README.md (not an allowed topic)
    When smith fetches from that directory
    Then it raises RuntimeError with "No matching files"
    """
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "README.md").write_text("hello")

    with pytest.raises(RuntimeError, match="No matching files"):
        fetch(str(empty))


def test_fetch_detect_top_dir() -> None:
    """
    Given a zip archive with entries "temple8-main/AGENTS.md" and
    "temple8-main/.opencode/agents/default.md"
    When smith extracts the archive
    Then file specs have paths "AGENTS.md" and ".opencode/agents/default.md"
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("temple8-main/AGENTS.md", "# agents")
        zf.writestr("temple8-main/.opencode/agents/default.md", "default")
    content = buf.getvalue()

    specs = _extract_zip(content)
    rel_paths = [str(s.relative_path) for s in specs]
    assert "AGENTS.md" in rel_paths
    assert any(".opencode" in p for p in rel_paths)
