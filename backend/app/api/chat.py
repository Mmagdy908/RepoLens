"""Chat API — Feature 1.3 (Nova Client + LangGraph Agent).

Accepts a ChatRequest, builds an AgentState from the session, and streams
the assistant reply as Server-Sent Events (SSE).

Routes
------
POST /api/chat   → StreamingResponse (text/event-stream)

SSE event shapes
----------------
  {"type": "step",  "content": "<msg>"}   — emitted on graph start and each tool invocation
  {"type": "text",  "chunk": "<token>"}   — final-answer token (agent-node LLM, no tool calls)
  {"type": "done"}                        — end-of-stream; session history persisted
  {"type": "error", "detail": "<msg>"}    — unhandled exception

Note: nova-2-lite-v1 does not stream reasoning tokens on tool-call passes, so
there is no "thinking" event type — tool-call passes produce empty content chunks
and are surfaced only via the "step" label emitted on on_tool_start.
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
# Human-readable reasoning statements shown to the user while a tool runs.
# Keyed by the exact @tool function name.
# ---------------------------------------------------------------------------
_TOOL_REASONING: dict[str, str] = {
    "get_project_overview": "Reading the codebase to build a project overview…",
    "get_tech_stack": "Scanning dependencies and configs to identify the tech stack…",
    "get_architecture_analysis": "Analysing the architectural structure of the codebase…",
    "find_design_flaws": "Inspecting the code for design flaws and anti-patterns…",
    "get_security_concerns": "Reviewing the codebase for potential security concerns…",
    "get_tech_debt_summary": "Looking for technical debt and areas that need refactoring…",
    "generate_architecture_diagram": "Generating a high-level architecture diagram…",
    "generate_component_diagram": "Generating a component relationship diagram…",
    "generate_sequence_diagram": "Generating a sequence diagram for the requested flow…",
    "get_file_explanation": "Examining the requested file in detail…",
    "get_folder_explanation": "Exploring the requested folder and its contents…",
    "answer_general_question": "Searching the codebase to answer your question…",
}

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
- Be concise: prefer short, precise answers over long explanations unless \
the user explicitly asks for detail.

Grounding rules — you MUST follow these at all times:
- NEVER assert file paths, function names, class names, variable names, \
library names, version numbers, or architectural details that are not \
directly evidenced in the repository context or tool results.
- NEVER fill gaps with general knowledge about how projects "typically" work. \
If something is not in the context, say explicitly that you cannot find it \
in the provided codebase.
- NEVER invent examples, hypothetical code snippets, or fictional module \
names to illustrate a point.
- If a tool result is incomplete or ambiguous, surface that uncertainty \
to the user rather than guessing.

You are given the repo context in the agent state. Use it to answer questions and decide which tools to call. \
"""


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """Stream the LangGraph agent reply as Server-Sent Events.

    Each SSE event carries a typed JSON payload — see module docstring for shapes.
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
        "repo_context": session.repo_context,
        "messages": history + [new_message],
    }

    async def event_stream():
        """Async generator that streams SSE chunks from the LangGraph agent."""
        full_content_parts: list[str] = []
        try:
            async for event in compiled_graph.astream_events(
                initial_state, version="v2"
            ):
                event_type = event["event"]
                metadata = event.get("metadata", {})
                response = ""
                if event_type == "on_chain_start" and event.get("name") == "LangGraph":
                    response = f"data: {json.dumps({'type': 'step', 'content': '🤔 Analysing your question...'})}\n\n"

                # ── Tool call started: emit a human-readable reasoning step ──
                elif event_type == "on_tool_start":
                    tool_name = event.get("name", "")
                    reasoning = _TOOL_REASONING.get(
                        tool_name, f"Running analysis using `{tool_name}`…"
                    )
                    response = f"data: {json.dumps({'type': 'step', 'content': reasoning})}\n\n"

                # ── Final-answer tokens: only from the top-level agent node ──
                elif event_type == "on_chat_model_stream":
                    if metadata.get("langgraph_node") != "agent":
                        continue
                    chunk = event["data"].get("chunk")
                    if chunk is None:
                        continue
                    token = chunk.content if hasattr(chunk, "content") else ""
                    if token:
                        full_content_parts.append(token)
                        response = f"data: {json.dumps({'type': 'chunk', 'content': token})}\n\n"
                if response:
                    yield response

            # Stream finished — persist the updated message history.
            # We need the final graph state; re-invoke synchronously would double-call,
            # so we reconstruct the AI message from the collected tokens instead and
            # append it to the session manually.

            ai_message = AIMessage(content="".join(full_content_parts))
            # print(ai_message.content)

            session.messages = initial_state["messages"] + [ai_message]

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            payload = json.dumps({"type": "error", "detail": str(exc)})
            yield f"data: {payload}"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
