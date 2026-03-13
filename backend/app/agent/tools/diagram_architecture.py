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
                    "Your ONLY output must be a single Mermaid fenced code block using `architecture-beta` for system diagrams, or `graph TD` as fallback.\n"
                    "Do NOT include any prose, headings, or explanation — just the fence.\n\n"
                    "Diagram Guidelines:\n"
                    "- Prefer `architecture-beta` syntax for high-level service/cloud architecture.\n"
                    "- Diagram must be HIGH-LEVEL and interpretable by humans. Do NOT include implementation details (e.g., individual files, classes, or utility functions).\n"
                    "- Focus on **major components/services**, **external dependencies**, **databases**, and **significant data flows**.\n\n"
                    "Use as few connections as needed. Do not make the diagram too complex or cluttered. It's better to omit some connections than to include too many and sacrifice clarity.\n\n"
                    "Syntax for `architecture-beta`:\n"
                    "    - `service <id>(logos:<icon>)[Label]`\n"
                    "    - `service db(logos:aws-rds)[Database]`\n"
                    "    - Connections: `<id>:<side> --> <side>:<target_id>` (e.g., `web:R --> L:api`)\n"
                    "    - Groups: `group <groupId>(logos:<icon>)[Label]`\n\n"
                    # "Syntax for `graph TD` (fallback):\n"
                    "    - Use node shapes: `[(db)]` for databases, `([svc])` for services, `{{ui}}` for frontend.\n"
                    "    - Use `subgraph` to group layers.\n"
                    "    - Use `classDef` to color-code roles.\n\n"
                    "- Keep node labels concise (≤ 5 words).\n"
                    "- Accurately reflect the actual code structure but abstract away file-level details.\n"
                    "- Avoid making a node as a parent of itself creating a cycle.\n"
                    "- Do NOT invent components, services, or connections not present in the context.\n"
                    "- If a part of the architecture is unclear from the context, omit it rather than guessing.\n\n"
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
