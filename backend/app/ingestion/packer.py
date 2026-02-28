"""Context packer — Feature 1.2.

Turns a list of ``FileNode`` objects into a single packed string that fits
inside Nova's 1 M-token context window, respecting a configurable token budget.

Public API
----------
``pack_context(file_nodes, root, budget) -> (packed_string, total_tokens)``
"""

from pathlib import Path

from app.ingestion.token_counter import count_tokens
from app.models.session import FileNode

# ---------------------------------------------------------------------------
# Priority scoring — T4.2
# ---------------------------------------------------------------------------
# Rules (higher score = included earlier):
#   main.*, index.*, app.*             → 100
#   *.config.*, *.toml, *.json, *.yaml → 80
#   files anywhere under src/          → 60
#   test* / *_test.* / *spec*          → 20
#   dist/, build/, generated/          → 5
#   everything else                    → 40
# ---------------------------------------------------------------------------

_ENTRY_POINT_STEMS = {"main", "index", "app"}
_CONFIG_SUFFIXES = {".toml", ".json", ".yaml", ".yml"}
_CONFIG_INFIX = ".config."
_LOW_SCORE_DIRS = {"dist", "build", "generated"}
_TEST_PREFIXES = ("test", "spec")
_TEST_SUFFIXES = ("_test", "_spec", ".test", ".spec")


def _priority_score(path: str) -> int:
    """Return a priority score for a given relative file path string."""
    parts = Path(path).parts  # e.g. ('src', 'models', 'user.py')
    name = Path(path).name  # e.g. 'user.py'
    stem = Path(path).stem  # e.g. 'user'
    suffix = Path(path).suffix.lower()  # e.g. '.py'

    # Lowest priority: dist / build / generated anywhere in the path
    if any(part.lower() in _LOW_SCORE_DIRS for part in parts):
        return 5

    # Tests
    lower_stem = stem.lower()
    if lower_stem.startswith(_TEST_PREFIXES) or lower_stem.endswith(_TEST_SUFFIXES):
        return 20

    # Entry points: main.*, index.*, app.*
    if lower_stem in _ENTRY_POINT_STEMS:
        return 100

    # Config files
    if suffix in _CONFIG_SUFFIXES or _CONFIG_INFIX in name.lower():
        return 80

    # Files under src/
    if parts and parts[0].lower() in ["src", "app"]:
        return 60

    # Default
    return 40


# ---------------------------------------------------------------------------
# Public function — T4.1
# ---------------------------------------------------------------------------


def pack_context(
    file_nodes: list[FileNode],
    root: Path,
    budget: int = 750_000,
) -> tuple[str, int]:
    """Pack ``file_nodes`` into a single context string within ``budget`` tokens.

    Parameters
    ----------
    file_nodes:
        List of ``FileNode`` objects produced by ``ingestion/filter.py``.
        Binary files (``is_binary=True``) are skipped automatically.
    root:
        Absolute path to the repository root on disk.  Used to read file
        content when ``FileNode.token_count`` is zero (i.e. the file was
        filtered but not yet counted).
    budget:
        Maximum number of tokens to include in the packed string.
        Defaults to 750 000 (the Phase 1 cap defined in the architecture).

    Returns
    -------
    packed_string:
        Concatenated file contents with ``=== FILE: {path} ===`` headers.
    total_tokens:
        Actual token count of the returned string.
    """
    # Sort descending by priority score, then alphabetically for stability.
    sorted_nodes = sorted(
        (n for n in file_nodes if not n.is_binary),
        key=lambda n: (-_priority_score(n.path), n.path),
    )  # ------------------------------------------------------------------
    # Build file list for the preamble (before we know what fits).
    # We use sorted_nodes order so the preamble reflects pack priority.
    # ------------------------------------------------------------------
    file_listing = "\n".join(f"  - {n.path}" for n in sorted_nodes)
    included_count = len(sorted_nodes)

    preamble = f"""\
=== REPOLENS CONTEXT BLOCK ===
You are an expert software engineer and code analyst.
The following is the **complete source code** of a software repository, \
packed into a single context window for your analysis.

INSTRUCTIONS:
- Answer questions about this codebase with precision, citing specific files \
and line ranges where relevant.
- When asked for a diagram, output ONLY a fenced Mermaid code block \
(```mermaid ... ```) with no surrounding prose unless asked.
- When referencing a file, always use the exact relative path shown in the \
=== FILE: ... === headers below.
- Do not hallucinate files or functions that are not present in the context.
- If the context does not contain enough information to answer, say so \
explicitly rather than guessing.

REPOSITORY CONTENTS ({included_count} files packed, budget {budget:,} tokens):
{file_listing}
=== END OF PREAMBLE ===
"""

    parts: list[str] = [preamble]
    total_tokens = count_tokens(preamble)

    for node in sorted_nodes:
        file_path = root / node.path
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        header = f"=== FILE: {node.path} ===\n"
        chunk = header + content + "\n"

        # Use cached token count when available; fall back to counting now.
        chunk_tokens = node.token_count if node.token_count > 0 else count_tokens(chunk)

        if total_tokens + chunk_tokens > budget:
            # Budget exhausted — stop packing.
            break

        parts.append(chunk)
        total_tokens += chunk_tokens

    packed_string = "\n".join(parts)
    return packed_string, total_tokens
