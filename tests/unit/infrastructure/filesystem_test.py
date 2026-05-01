import contextlib
from pathlib import Path

from smith.domain.value_objects import FileSpec
from smith.infrastructure.filesystem import AtomicFileSystem, FileSystemError


class TestAtomicFileSystem:
    def test_write_atomic_creates_files(self, tmp_path: Path) -> None:
        fs = AtomicFileSystem(tmp_path)
        specs = [
            FileSpec(relative_path=Path("AGENTS.md"), content=b"# Agents\n"),
            FileSpec(
                relative_path=Path(".opencode/config.yaml"),
                content=b"key: value\n",
            ),
        ]
        fs.write_atomic(specs)
        assert (tmp_path / "AGENTS.md").read_bytes() == b"# Agents\n"
        assert (tmp_path / ".opencode/config.yaml").read_bytes() == b"key: value\n"

    def test_write_atomic_creates_parent_directories(self, tmp_path: Path) -> None:
        fs = AtomicFileSystem(tmp_path)
        specs = [FileSpec(relative_path=Path("a/b/c.txt"), content=b"deep\n")]
        fs.write_atomic(specs)
        assert (tmp_path / "a/b/c.txt").read_bytes() == b"deep\n"

    def test_write_atomic_replaces_existing_files(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"old content\n")
        fs = AtomicFileSystem(tmp_path)
        specs = [FileSpec(relative_path=Path("AGENTS.md"), content=b"new content\n")]
        fs.write_atomic(specs)
        assert (tmp_path / "AGENTS.md").read_bytes() == b"new content\n"

    def test_write_atomic_is_atomic_on_failure(self, tmp_path: Path) -> None:
        fs = AtomicFileSystem(tmp_path)
        existing = tmp_path / "existing.txt"
        existing.write_bytes(b"keep me\n")
        specs = [
            FileSpec(relative_path=Path("good.txt"), content=b"good\n"),
            FileSpec(relative_path=Path("/dev/null/impossible.txt"), content=b"bad\n"),
        ]
        with contextlib.suppress(FileSystemError):
            fs.write_atomic(specs)
        assert existing.read_bytes() == b"keep me\n"
        assert not (tmp_path / "good.txt").exists()

    def test_check_conflicts_returns_conflicting_paths(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"existing\n")
        fs = AtomicFileSystem(tmp_path)
        conflicts = fs.check_conflicts([Path("AGENTS.md"), Path("new.txt")])
        assert Path("AGENTS.md") in conflicts
        assert Path("new.txt") not in conflicts

    def test_check_conflicts_returns_empty_when_no_conflicts(
        self, tmp_path: Path
    ) -> None:
        fs = AtomicFileSystem(tmp_path)
        conflicts = fs.check_conflicts([Path("AGENTS.md"), Path("new.txt")])
        assert conflicts == []

    def test_exists_returns_dict(self, tmp_path: Path) -> None:
        (tmp_path / "AGENTS.md").write_bytes(b"exists\n")
        fs = AtomicFileSystem(tmp_path)
        result = fs.exists([Path("AGENTS.md"), Path("missing.txt")])
        assert result[Path("AGENTS.md")] is True
        assert result[Path("missing.txt")] is False

    def test_remove_deletes_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_bytes(b"a\n")
        (tmp_path / "b.txt").write_bytes(b"b\n")
        fs = AtomicFileSystem(tmp_path)
        fs.remove([Path("a.txt")])
        assert not (tmp_path / "a.txt").exists()
        assert (tmp_path / "b.txt").exists()

    def test_remove_nonexistent_does_not_raise(self, tmp_path: Path) -> None:
        fs = AtomicFileSystem(tmp_path)
        fs.remove([Path("nonexistent.txt")])

    def test_write_atomic_with_empty_specs_does_nothing(self, tmp_path: Path) -> None:
        fs = AtomicFileSystem(tmp_path)
        fs.write_atomic([])
        assert list(tmp_path.iterdir()) == []
