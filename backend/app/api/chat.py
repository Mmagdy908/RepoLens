"""Chat API — Feature 1.3 (Nova Client + LangGraph Agent).

Accepts a ChatRequest, builds an AgentState from the session, invokes the
compiled LangGraph and returns the assistant reply as a plain JSON response.
Streaming (SSE) is added in T5.13.

Routes
------
POST /api/chat   → ChatResponse (200)
"""

import asyncio

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.graph import compiled_graph
from app.api.sessions import _sessions
from app.models.chat import ChatRequest, ChatResponse

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
"""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Invoke the LangGraph agent and return the final assistant message.

    Raises 404 if the session does not exist.
    Raises 500 if the agent fails unexpectedly.
    """
    session = _sessions.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Session '{request.session_id}' not found."
        )

    # Build LangGraph initial state from the session + the new user message.
    # Existing messages are carried over so the agent has conversation history.
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

    # Run the graph in a thread pool — compiled_graph.invoke() is synchronous.
    loop = asyncio.get_event_loop()
    try:
        final_state = await loop.run_in_executor(
            None, compiled_graph.invoke, initial_state
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    # Persist the updated message history back into the session.
    session.messages = final_state["messages"]

    # The last message is the assistant's final reply.
    last_message = final_state["messages"][-1]
    content = (
        last_message.content if hasattr(last_message, "content") else str(last_message)
    )

    return ChatResponse(content=content, role="assistant")
