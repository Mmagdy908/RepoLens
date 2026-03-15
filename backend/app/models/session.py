from typing import Optional
from pydantic import BaseModel, Field


class FileNode(BaseModel):
    """A single file discovered during repo ingestion

    Produced by ``ingestion/filter.py`` and stored inside ``SessionState.file_tree``.
    Binary files are included with ``is_binary=True`` so the frontend can show
    them in the tree without attempting to display their content.
    """

    path: str = Field(..., description="Relative path from the repo root.")
    size_bytes: int = Field(..., description="File size in bytes.")
    # Populated by token_counter.py (Feature 1.2) after ingestion.
    token_count: int = Field(0, description="Token count for the file content.")
    language: Optional[str] = Field(None, description="Detected programming language.")
    is_binary: bool = Field(False, description="True if the file is binary.")


class SessionState(BaseModel):
    """Full in-memory state for an active analysis session.

    One instance lives in the FastAPI process's ``sessions`` dict
    (keyed by ``session_id``) for the lifetime of the session.  No database is
    used in Phase 1 — state is lost on server restart.

    Lifecycle:
      1. Created by ``POST /api/ingest`` after ingestion completes (Feature 1.1).
      2. ``repo_context`` and ``token_count`` are populated by the context packer
         (Feature 1.2).
      3. ``messages`` grows with every chat turn handled by the LangGraph agent
         (Feature 1.3).
    """

    session_id: str = Field(..., description="UUID that identifies this session.")
    repo_url: Optional[str] = Field(
        None, description="GitHub URL that was ingested, if any."
    )

    file_tree: list[FileNode] = Field(
        default_factory=list, description="All non-binary files in the repo."
    )

    repo_context: Optional[str] = Field(
        None, description="Packed codebase string sent to Nova."
    )
    token_count: int = Field(0, description="Total tokens in the packed context.")
    token_budget: int = Field(
        750_000, description="Maximum tokens allowed in the context."
    )

    messages: list[dict] = Field(
        default_factory=list, description="Chat history (LangGraph message dicts)."
    )


class SessionSummary(BaseModel):
    """Lightweight DTO returned by ``GET /api/sessions/{id}``.

    Omits ``repo_context`` and ``messages`` so the response stays small even
    when the packed codebase is hundreds of thousands of tokens.  The frontend
    uses ``token_count`` / ``token_budget`` to render the token-usage bar
    (Feature 1.6 — ``TokenUsageBar`` component).
    """

    session_id: str
    repo_url: Optional[str]
    token_count: int
    token_budget: int
    # Derived from len(SessionState.file_tree) at serialisation time.
    file_count: int
