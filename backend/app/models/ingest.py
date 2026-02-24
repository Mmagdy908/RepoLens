from typing import Optional

from pydantic import BaseModel, Field

from app.models.session import FileNode


class IngestRequest(BaseModel):
    url: Optional[str] = Field(
        None,
        description="Public GitHub repository URL to clone and ingest.",
    )

    zip_filename: Optional[str] = Field(
        None,
        description="Filename of an already-uploaded zip archive to ingest.",
    )


class IngestResponse(BaseModel):
    session_id: str = Field(
        ..., description="UUID for the new session created after ingestion."
    )

    file_tree: list[FileNode] = Field(
        default_factory=list,
        description="List of all non-binary files discovered during ingestion.",
    )

    token_count: int = Field(
        0, description="Total token count for all files in the repo."
    )

    token_budget: int = Field(
        750_000, description="Maximum tokens allowed in the context."
    )
