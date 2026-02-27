"""Sessions API — Feature 1.7 (FastAPI Backend Skeleton).

In-memory session store: Dict[session_id, SessionState].
No database is used in Phase 1; state is lost on server restart.

Routes
------
GET    /api/sessions/{id}       → retrieve session summary (200 | 404)
DELETE /api/sessions/{id}       → delete session (204 | 404)
"""

from fastapi import APIRouter, HTTPException

from app.models.session import SessionState, SessionSummary

router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# In-memory store — module-level singleton, shared across all requests.
# Keyed by session_id (UUID string).
# ---------------------------------------------------------------------------
_sessions: dict[str, SessionState] = {}


def _to_summary(session: SessionState) -> SessionSummary:
    return SessionSummary(
        session_id=session.session_id,
        repo_url=session.repo_url,
        token_count=session.token_count,
        token_budget=session.token_budget,
        file_count=len(session.file_tree),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/sessions/{session_id}", response_model=SessionSummary)
def get_session(session_id: str) -> SessionSummary:
    """Retrieve a session summary by ID."""
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Session '{session_id}' not found."
        )
    return _to_summary(session)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str) -> None:
    """Delete a session by ID."""
    if session_id not in _sessions:
        raise HTTPException(
            status_code=404, detail=f"Session '{session_id}' not found."
        )
    del _sessions[session_id]
