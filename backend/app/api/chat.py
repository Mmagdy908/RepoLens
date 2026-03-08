"""Chat API — Feature 1.3 (Nova Client + LangGraph Agent).

Accepts a ChatRequest, builds an AgentState from the session, and streams
the assistant reply as Server-Sent Events (SSE).

Routes
------
POST /api/chat   → StreamingResponse (text/event-stream)
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from app.agent.graph import compiled_graph
from app.api.sessions import _sessions
from app.models.chat import ChatRequest

router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------------
# System prompt — prepended once at the start of every new session.
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are RepoLens, an expert AI software engineer and code analyst.
You have been given full access to a software repository and a set of \
specialised tools to analyse it.

Your responsibilities:
- Answer questions about the codebase accurately and concisely.
- Use the available tools whenever a question requires inspecting the repo \
(overviews, tech stack, architecture, file/folder explanations, diagrams, \
design analysis). Do NOT answer from general knowledge when a tool can give \
a grounded answer.
- Format all responses in Markdown. Use headers, bullet points, and code \
blocks where appropriate.
- When generating diagrams, output only valid Mermaid syntax inside a \
fenced code block (```mermaid ... ```).
- Never hallucinate file paths, function names, or library versions — only \
assert things you can verify from the repository context.
- Be concise: prefer short, precise answers over long explanations unless \
the user explicitly asks for detail.

You are given the repo context if needed in the agent state. Use it to answer questions and decide which tools to call. \
"""


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """Stream the LangGraph agent reply as Server-Sent Events.

    Each SSE event carries a JSON payload:
      {"type": "chunk", "content": "<token>"}   — incremental text token
      {"type": "done"}                           — signals end-of-stream
      {"type": "error", "detail": "<message>"}  — agent error

    Raises 404 if the session does not exist.
    """
    session = _sessions.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Session '{request.session_id}' not found."
        )

    # Build LangGraph initial state from the session + the new user message.
    # On the very first turn, prepend the system prompt so the LLM knows its
    # identity and rules for the entire session.
    new_message = HumanMessage(content=request.message)
    history = list(session.messages)
    if not history:
        history = [SystemMessage(content=_SYSTEM_PROMPT)]

    initial_state = {
        "session_id": session.session_id,
        "repo_context": session.repo_context or "",
        "messages": history + [new_message],
    }

    async def event_stream():
        """Async generator that streams SSE chunks from the LangGraph agent."""
        full_content_parts: list[str] = []
        try:
            async for event in compiled_graph.astream_events(
                initial_state, version="v2"
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if chunk is None:
                        continue
                    token = chunk.content if hasattr(chunk, "content") else ""
                    if token:
                        full_content_parts.append(token)
                        payload = json.dumps({"type": "chunk", "content": token})
                        yield f"data: {payload}\n\n"

            # Stream finished — persist the updated message history.
            # We need the final graph state; re-invoke synchronously would double-call,
            # so we reconstruct the AI message from the collected tokens instead and
            # append it to the session manually.

            ai_message = AIMessage(content="".join(full_content_parts))
            print(ai_message.content)

            session.messages = initial_state["messages"] + [ai_message]

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            payload = json.dumps({"type": "error", "detail": str(exc)})
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
