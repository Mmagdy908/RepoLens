"""

Usage
-----
    from app.ingestion.cloner import clone_from_url
    root = clone_from_url("https://github.com/owner/repo")
    # root is a pathlib.Path pointing at the cloned directory
"""

import tempfile
from pathlib import Path

import git


def clone_from_url(url: str) -> Path:
    """Shallow-clone *url* (depth=1) into a fresh temp directory.

    Parameters
    ----------
    url:
        A valid GitHub (or any git-hosting) HTTPS URL, e.g.
        ``https://github.com/owner/repo`` or
        ``https://github.com/owner/repo.git``.

    Returns
    -------
    Path
        Absolute path to the root of the cloned repository.

    Raises
    ------
    git.GitCommandError
        If the clone fails (bad URL, auth error, network issue, etc.).
    """
    tmp_dir = tempfile.mkdtemp(prefix="repolens_clone_")
    git.Repo.clone_from(
        url,
        tmp_dir,
        # Suppress progress output — we don't want it in server logs.
        env={"GIT_TERMINAL_PROMPT": "0"},
    )
    return Path(tmp_dir)
