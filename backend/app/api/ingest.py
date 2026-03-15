"""
Accepts either a JSON body (GitHub URL) or a multipart file upload (zip).
Runs the full ingestion pipeline:
  clone / extract  →  filter_files  →  count_tokens per file  →  store session

"""

import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.sessions import _sessions
from app.ingestion.cloner import clone_from_url
from app.ingestion.extractor import extract_zip
from app.ingestion.filter import filter_files
from app.ingestion.packer import pack_context
from app.ingestion.token_counter import count_tokens
from app.models.ingest import IngestRequest, IngestResponse
from app.models.session import SessionState

router = APIRouter(prefix="/api")


async def _run_pipeline(root: Path, repo_url: str | None) -> SessionState:
    """Run filter → token-count in a thread pool (blocking I/O + CPU work)."""

    def _blocking() -> SessionState:
        nodes = filter_files(root)

        # Count tokens for each non-binary file.
        for node in nodes:
            if node.is_binary:
                continue
            try:
                text = (root / node.path).read_text(encoding="utf-8", errors="replace")
                node.token_count = count_tokens(text)
            except OSError:
                node.token_count = 0

        # Pack the context string within the 750k-token budget (T4.3).
        packed_string, packed_tokens = pack_context(nodes, root, budget=750_000)

        session_id = str(uuid4())
        return SessionState(
            session_id=session_id,
            repo_url=repo_url,
            file_tree=nodes,
            repo_context=packed_string,
            token_count=packed_tokens,
            token_budget=750_000,
        )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _blocking)


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest_url(request: IngestRequest) -> IngestResponse:
    """Accept a JSON body with a GitHub URL, run the ingestion pipeline,
    and return an ``IngestResponse`` with the file tree and token count.
    """
    if not request.url:
        raise HTTPException(
            status_code=422,
            detail="Field 'url' is required for URL-based ingestion.",
        )

    try:
        root = await asyncio.get_event_loop().run_in_executor(
            None, clone_from_url, request.url
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to clone repository: {exc}",
        ) from exc

    try:
        session = await _run_pipeline(root, request.url)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline error: {exc}",
        ) from exc

    _sessions[session.session_id] = session

    return IngestResponse(
        session_id=session.session_id,
        file_tree=session.file_tree,
        token_count=session.token_count,
        token_budget=session.token_budget,
    )


@router.post("/ingest/upload", response_model=IngestResponse, status_code=201)
async def ingest_zip(file: UploadFile = File(...)) -> IngestResponse:
    """Accept a zip file upload, run the ingestion pipeline,
    and return an ``IngestResponse`` with the file tree and token count.
    """
    if file.content_type not in (
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream",
    ):
        # Be lenient — some browsers send a generic content type.
        pass

    try:
        zip_bytes = await file.read()
        root = await asyncio.get_event_loop().run_in_executor(
            None, extract_zip, zip_bytes
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract zip archive: {exc}",
        ) from exc

    try:
        session = await _run_pipeline(root, None)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline error: {exc}",
        ) from exc

    _sessions[session.session_id] = session
    return IngestResponse(
        session_id=session.session_id,
        file_tree=session.file_tree,
        token_count=session.token_count,
        token_budget=session.token_budget,
    )
