"""File filter — Feature 1.1 (Repo Ingestion Engine).

Provides ``filter_files`` which walks a repo tree, skips ignored paths, and
returns a list of ``FileNode`` objects for files that should be ingested.

Ignore rules (applied in priority order)
-----------------------------------------
1. Hard-coded default ignores (``ALWAYS_IGNORE_DIRS`` / ``ALWAYS_IGNORE_PATTERNS``).
2. ``.repolensignore`` file at the repo root (pathspec gitignore syntax).
3. Standard ``.gitignore`` at the repo root.
4. Binary-file detection: read the first 512 bytes; if a null byte is found
   the file is marked ``is_binary=True`` and excluded from context packing
   (but still returned so the frontend can show it in the tree).

Usage
-----
    from app.ingestion.filter import filter_files
    nodes = filter_files(Path("/tmp/cloned_repo"))
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pathspec

from app.models.session import FileNode

# ---------------------------------------------------------------------------
# Hard-coded exclusions — these are never ingested regardless of ignore files.
# ---------------------------------------------------------------------------

ALWAYS_IGNORE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".next",
        "out",
        "coverage",
        ".venv",
        "venv",
        ".tox",
        ".eggs",
        "*.egg-info",
    }
)

ALWAYS_IGNORE_PATTERNS: list[str] = [
    # Lock files
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    # Compiled / generated artifacts
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.exe",
    "*.class",
    "*.o",
    "*.a",
    # Media / binary assets
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.svg",
    "*.mp4",
    "*.mov",
    "*.mp3",
    "*.wav",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.whl",
    # IDE / OS noise
    ".DS_Store",
    "Thumbs.db",
    "*.swp",
    "*.swo",
]

# ---------------------------------------------------------------------------
# Language detection (best-effort, by extension)
# ---------------------------------------------------------------------------

_EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".kt": "kotlin",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".ps1": "powershell",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown",
    ".mdx": "markdown",
    ".rst": "rst",
    ".sql": "sql",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".proto": "protobuf",
    ".tf": "terraform",
    ".hcl": "hcl",
    ".dockerfile": "dockerfile",
}


def _detect_language(path: Path) -> Optional[str]:
    """Return a language label based on file extension, or ``None``."""
    if path.name.lower() in ("dockerfile", "makefile", "vagrantfile"):
        return path.name.lower()
    return _EXT_TO_LANG.get(path.suffix.lower())


def _is_binary(path: Path) -> bool:
    """Return ``True`` if the file looks binary (contains a null byte in the
    first 512 bytes)."""
    try:
        with path.open("rb") as fh:
            chunk = fh.read(512)
        return b"\x00" in chunk
    except OSError:
        return True


def _load_spec(root: Path, filename: str) -> Optional[pathspec.PathSpec]:
    """Load a pathspec from *filename* at *root*, or return ``None``."""
    ignore_file = root / filename
    if not ignore_file.is_file():
        return None
    lines = ignore_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def filter_files(root: Path) -> list[FileNode]:
    """Walk *root* and return a list of ``FileNode`` objects.

    Binary files are included in the returned list with ``is_binary=True`` so
    the frontend can display them in the file explorer.  Their ``token_count``
    will remain 0 — the context packer skips binary files.

    Parameters
    ----------
    root:
        Absolute path to the repository root.

    Returns
    -------
    list[FileNode]
        Sorted (by relative path) list of file nodes.
    """
    # Build the combined ignore spec from hard-coded patterns + user files.
    all_patterns = list(ALWAYS_IGNORE_PATTERNS)
    default_spec = pathspec.PathSpec.from_lines("gitwildmatch", all_patterns)
    repolens_spec = _load_spec(root, ".repolensignore")
    gitignore_spec = _load_spec(root, ".gitignore")

    nodes: list[FileNode] = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root)

        # Prune ignored directories in-place (modifies os.walk's iteration).
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ALWAYS_IGNORE_DIRS
            and not default_spec.match_file(str(rel_dir / d) + "/")
            and (
                repolens_spec is None
                or not repolens_spec.match_file(str(rel_dir / d) + "/")
            )
            and (
                gitignore_spec is None
                or not gitignore_spec.match_file(str(rel_dir / d) + "/")
            )
        ]

        for filename in filenames:
            abs_path = current_dir / filename
            rel_path = abs_path.relative_to(root)
            rel_str = str(rel_path).replace("\\", "/")

            # Apply pattern-based ignore rules.
            if default_spec.match_file(rel_str):
                continue
            if repolens_spec and repolens_spec.match_file(rel_str):
                continue
            if gitignore_spec and gitignore_spec.match_file(rel_str):
                continue

            try:
                size = abs_path.stat().st_size
            except OSError:
                continue

            binary = _is_binary(abs_path)
            lang = _detect_language(abs_path) if not binary else None

            nodes.append(
                FileNode(
                    path=rel_str,
                    size_bytes=size,
                    token_count=0,  # Populated later by token_counter.py
                    language=lang,
                    is_binary=binary,
                )
            )

    nodes.sort(key=lambda n: n.path)
    return nodes
