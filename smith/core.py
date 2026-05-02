"""Core logic for clone and purge operations."""

import io
import os
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import requests

from smith.gitignore import GitignoreManager

DEFAULT_SOURCE = "github:nullhack/temple8"

ALLOWED_TOPICS = ("AGENTS.md", ".opencode/", ".flowr/", ".templates/")


@dataclass(frozen=True)
class FileSpec:
    relative_path: Path
    content: bytes


def resolve_source(source_arg: str | None, project_dir: Path) -> str:
    """Resolve the template source from CLI arg, pyproject.toml, or default."""
    if source_arg is not None:
        return source_arg
    config_path = project_dir / "pyproject.toml"
    if config_path.exists():
        try:
            import tomllib

            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            source = data.get("tool", {}).get("smith", {}).get("source")
            if source:
                return source
        except Exception:
            pass
    return DEFAULT_SOURCE


def _is_allowed(path: Path) -> bool:
    """Check if a relative path matches one of the allowed topic prefixes."""
    path_str = str(path)
    for prefix in ALLOWED_TOPICS:
        if prefix.endswith("/"):
            if path_str == prefix.rstrip("/") or path_str.startswith(prefix):
                return True
        else:
            if path_str == prefix:
                return True
    return False


def _top_level_patterns(specs: list[FileSpec]) -> list[str]:
    """Derive gitignore patterns from the top-level directories and files in specs."""
    seen: set[str] = set()
    for spec in specs:
        parts = spec.relative_path.parts
        seen.add(parts[0] + ("/" if len(parts) > 1 else ""))
    return sorted(seen)


def fetch(source: str) -> list[FileSpec]:
    """Fetch file specs from the given source string."""
    if source.startswith("github:"):
        repo = source[len("github:") :]
        return _fetch_github(repo)
    if source.startswith("http://") or source.startswith("https://"):
        if "github.com" in source:
            repo = _parse_github_url(source)
            if repo:
                return _fetch_github(repo)
        return _fetch_url(source)
    return _fetch_local(Path(source))


def _parse_github_url(url: str) -> str | None:
    """Extract user/repo from a github.com URL."""
    parts = url.rstrip("/").split("/")
    for i, part in enumerate(parts):
        if part == "github.com" and i + 2 < len(parts):
            return f"{parts[i + 1]}/{parts[i + 2]}"
    return None


def _fetch_github(repo: str) -> list[FileSpec]:
    """Download and extract files from a GitHub repo."""
    url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            url = f"https://github.com/{repo}/archive/refs/heads/master.zip"
            response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to download from GitHub: {repo}") from exc
    return _extract_zip(response.content)


def _fetch_url(url: str) -> list[FileSpec]:
    """Download and extract files from a URL (zip or tar.gz)."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to download from {url}") from exc
    if url.endswith(".zip"):
        return _extract_zip(response.content)
    return _extract_tar(response.content)


def _fetch_local(path: Path) -> list[FileSpec]:
    """Walk a local directory and collect file specs."""
    if not path.is_dir():
        raise RuntimeError(f"Template directory not found: {path}")
    specs: list[FileSpec] = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(path)
            if _is_allowed(rel):
                specs.append(FileSpec(relative_path=rel, content=full.read_bytes()))
    if not specs:
        raise RuntimeError(f"No matching files found in: {path}")
    return specs


def _detect_top_dir(names: list[str]) -> str | None:
    """Detect a single common top-level directory in archive entries."""
    top_dirs: set[str] = set()
    for name in names:
        if "/" not in name:
            return None
        top_dirs.add(name.split("/")[0])
    if len(top_dirs) == 1:
        return next(iter(top_dirs))
    return None


def _extract_zip(content: bytes) -> list[FileSpec]:
    """Extract a zip archive and return filtered file specs."""
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        if not names:
            raise RuntimeError("Zip archive is empty")
        prefix = _detect_top_dir(names)
        prefix_len = len(prefix) + 1 if prefix else 0
        specs: list[FileSpec] = []
        for name in names:
            rel = name[prefix_len:] if prefix_len else name
            if not rel:
                continue
            path = Path(rel)
            if _is_allowed(path):
                specs.append(FileSpec(relative_path=path, content=zf.read(name)))
        if not specs:
            raise RuntimeError("No matching files found in zip archive")
        return specs


def _extract_tar(content: bytes) -> list[FileSpec]:
    """Extract a tar.gz archive and return filtered file specs."""
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        if not members:
            raise RuntimeError("Tar archive is empty")
        names = [m.name for m in members]
        prefix = _detect_top_dir(names)
        prefix_len = len(prefix) + 1 if prefix else 0
        specs: list[FileSpec] = []
        for member in members:
            rel = member.name[prefix_len:] if prefix_len else member.name
            if not rel:
                continue
            path = Path(rel)
            if _is_allowed(path):
                specs.append(
                    FileSpec(relative_path=path, content=tar.extractfile(member).read())
                )
        if not specs:
            raise RuntimeError("No matching files found in tar archive")
        return specs


def clone(project_dir: Path, source: str, overwrite: bool = False) -> None:
    """Clone template files into a project directory."""
    specs = fetch(source)
    if not specs:
        raise RuntimeError(f"No matching files found in source: {source}")

    skip_items: set[str] = set()
    if not overwrite:
        for dirname in (".opencode", ".flowr", ".templates"):
            if (project_dir / dirname).is_dir():
                skip_items.add(dirname)
        if (project_dir / "AGENTS.md").exists():
            skip_items.add("AGENTS.md")

    written_specs: list[FileSpec] = []
    for spec in specs:
        top = spec.relative_path.parts[0]
        if top in skip_items:
            continue
        dest = project_dir / spec.relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(spec.content)
        written_specs.append(spec)

    if written_specs:
        patterns = _top_level_patterns(written_specs)
        manager = GitignoreManager(project_dir)
        manager.add_section(patterns)


def purge(project_dir: Path) -> list[Path]:
    """Delete files/folders listed in the smith-managed .gitignore section."""
    manager = GitignoreManager(project_dir)
    if not manager.has_section():
        return []

    patterns = manager.get_patterns()
    if not patterns:
        return []

    removed: list[Path] = []
    for pattern in patterns:
        path = project_dir / pattern.rstrip("/")
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(Path(pattern.rstrip("/")))
        elif path.exists():
            path.unlink()
            removed.append(Path(pattern))
    return removed
