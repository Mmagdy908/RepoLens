from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        ..., description="UUID of the session to which this chat message belongs."
    )
    message: str = Field(
        ..., description="The user's message to be processed by the agent."
    )


class ChatResponse(BaseModel):
    """Response body for ``POST /api/chat``."""

    content: str = Field(..., description="The agent's response text.")
    role: str = Field(
        "assistant", description="The role of the message author (always 'assistant')."
    )
