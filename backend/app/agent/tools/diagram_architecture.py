import re
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count


def _extract_mermaid_fence(text: str) -> str:
    """Extract only the first Mermaid fenced block from the response.

    Returns the raw fence string (```mermaid … ```) if found,
    otherwise returns the full text as a fallback.
    """
    match = re.search(r"(```mermaid\s.*?```)", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


@tool
async def generate_architecture_diagram(
    focus: str,
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Generate a Mermaid graph TD architecture diagram for the repository.

    Args:
        focus: Optional area of the codebase to focus on (e.g. "authentication",
               "data pipeline"). Leave empty for a full overview.
    """
    _tools_usage_count["diagram_architecture"] += 1

    focus_instruction = (
        f" Focus specifically on the '{focus}' subsystem." if focus else ""
    )

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert software architect analysing a code repository.\n"
                    "Your ONLY output must be a single Mermaid fenced code block using `graph TD` or `graph LR`.\n"
                    "Do NOT include any prose, headings, or explanation — just the fence.\n\n"
                    "Diagram rules:\n"
                    "- Choose node shapes that suit each component type "
                    "(e.g. cylinders `[(db)]` for databases, rounded `([svc])` for services, "
                    "rhombuses `{decision}` for branching)\n"
                    "- Use `subgraph` blocks to group related components by layer or domain\n"
                    "- Add short, meaningful edge labels on every arrow\n"
                    "- Use `classDef` + `class` to colour-code nodes by architectural role — "
                    "choose the colours yourself so they look professional and are easy to read\n"
                    "- Keep node labels concise (≤ 5 words)\n"
                    "- Accurately reflect the actual code structure\n"
                    "- Avoid making a node as a parent of itself creating a cycle\n"
                    "- Do NOT invent components, services, or connections not present in the context\n"
                    "- If a part of the architecture is unclear from the context, omit it rather than guessing\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate a Mermaid graph TD architecture diagram for this project.{focus_instruction}"
                ),
            },
        ],
    )

    raw = response.content or ""
    return _extract_mermaid_fence(raw)
