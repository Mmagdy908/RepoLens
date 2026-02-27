"""Ingest API — Feature 1.1 (Repo Ingestion Engine) — STUB.

Accepts either a JSON body (GitHub URL) or a multipart file upload (zip).
Returns a stub IngestResponse with a new session_id and empty file tree.

Real ingestion pipeline (clone / extract → filter → count tokens → pack
context) is wired in during Milestone 3 (T3.7).

Routes
------
POST /api/ingest   → IngestResponse (201)
"""

from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.sessions import _sessions
from app.models.ingest import IngestRequest, IngestResponse
from app.models.session import SessionState

router = APIRouter(prefix="/api")


@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(
    request: IngestRequest | None = None,
    file: UploadFile | None = File(default=None),
) -> IngestResponse:
    """Accept a GitHub URL (JSON body) or a zip UploadFile and return a stub
    IngestResponse.  Full ingestion is implemented in Milestone 3.
    """
    # Validate: exactly one source must be provided.
    has_url = request is not None and request.url is not None
    has_zip = file is not None

    if not has_url and not has_zip:
        raise HTTPException(
            status_code=422,
            detail="Provide either a JSON body with 'url' or a zip file upload.",
        )
    if has_url and has_zip:
        raise HTTPException(
            status_code=422,
            detail="Provide either a URL or a zip file, not both.",
        )

    # Create a new session and persist it in the shared in-memory store.
    session_id = str(uuid4())
    repo_url = request.url if has_url else None
    session = SessionState(session_id=session_id, repo_url=repo_url)
    _sessions[session_id] = session

    # --- STUB: real pipeline (clone → filter → pack) added in T3.7 ---
    return IngestResponse(
        session_id=session_id,
        file_tree=[],
        token_count=0,
        token_budget=750_000,
    )
