"""
Usage
-----
    from app.ingestion.extractor import extract_zip
    root = extract_zip(await upload_file.read())
"""

import tempfile
import zipfile
from io import BytesIO
from pathlib import Path


def extract_zip(data: bytes) -> Path:
    """Extract *data* (raw zip bytes) into a fresh temp directory.

    Many GitHub zip downloads wrap the repo contents in a single top-level
    directory (e.g. ``repo-main/``).  When that pattern is detected the
    function returns the path to that inner directory so callers always get
    the repo root, not a wrapper folder.

    Parameters
    ----------
    data:
        Raw bytes of a zip archive.

    Returns
    -------
    Path
        Absolute path to the repository root inside the extracted tree.

    Raises
    ------
    zipfile.BadZipFile
        If *data* is not a valid zip archive.
    """
    tmp_dir = tempfile.mkdtemp(prefix="repolens_zip_")
    tmp_path = Path(tmp_dir)

    with zipfile.ZipFile(BytesIO(data)) as zf:
        zf.extractall(tmp_path)

    # Detect GitHub-style single top-level wrapper folder.
    children = list(tmp_path.iterdir())
    if len(children) == 1 and children[0].is_dir():
        return children[0]

    return tmp_path
