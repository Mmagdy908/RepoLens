import re
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count


def _extract_mermaid_fence(text: str) -> str:
    """Extract only the first Mermaid fenced block from the response."""
    match = re.search(r"(```mermaid\s.*?```)", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


@tool
async def generate_sequence_diagram(
    flow: str,
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Generate a Mermaid sequenceDiagram for a specific flow in the repository.

    Args:
        flow: The interaction or flow to diagram (e.g. "user login",
              "file ingestion pipeline", "API request lifecycle").
    """
    _tools_usage_count["diagram_sequence"] += 1

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (                    "You are an expert software architect analysing a code repository.\n"
                    "Your ONLY output must be a single Mermaid fenced code block using `sequenceDiagram`.\n"
                    "Do NOT include any prose, headings, or explanation — just the fence.\n\n"
                    "Diagram rules:\n"
                    "- Keep participant names concise (≤ 3 words)\n"
                    "- Use `activate`/`deactivate` to highlight active lifelines\n"
                    "- Use `Note over` or `Note right of` for important clarifications\n"
                    "- Use `loop`, `alt`, `opt` blocks where they reflect real branching logic\n"
                    "- Label every arrow with a short, meaningful description\n"
                    "- Show only the key messages for the requested flow — avoid noise\n"
                    "- Accurately reflect the actual code\n"
                    "- Do NOT invent participants, messages, or flow steps not evidenced in the context\n"
                    "- If the requested flow is not clearly visible in the context, say so rather than fabricating a diagram\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate a Mermaid sequenceDiagram for the following flow in this project: {flow}"
                ),
            },
        ],
    )

    raw = response.content or ""
    return _extract_mermaid_fence(raw)
