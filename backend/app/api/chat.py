"""Chat API — Feature 1.3 (Nova Client + LangGraph Agent) — STUB.

Accepts a ChatRequest and returns a StreamingResponse that echoes the
message back as Server-Sent Events.  The real LangGraph agent is wired in
during Milestone 5 (T5.12 / T5.13).

Routes
------
POST /api/chat   → StreamingResponse (text/event-stream)
"""

import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.sessions import _sessions
from app.models.chat import ChatRequest

router = APIRouter(prefix="/api")


async def _echo_stream(message: str):
    """Yield each word of the message as an SSE chunk, then close the stream."""
    words = message.split()
    for word in words:
        yield f"data: {word} \n\n"
        await asyncio.sleep(0.05)
    yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """Echo the user's message back word-by-word as an SSE stream.

    Raises 404 if the session does not exist.  Full agent integration is
    implemented in Milestone 5.
    """
    if request.session_id not in _sessions:
        raise HTTPException(
            status_code=404, detail=f"Session '{request.session_id}' not found."
        )

    return StreamingResponse(
        _echo_stream(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
