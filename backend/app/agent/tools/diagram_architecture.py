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
                    "You are an expert software architect. Your goal is to simplify a complex repository into a clean, executive-level system architecture diagram.\n\n"
                    "### OUTPUT RULES:\n"
                    "- ONLY a single Mermaid `graph TD` code block.\n"
                    "- No prose or explanations.\n\n"
                    "### THE 'POWER OF 3' ABSTRACTION RULE:\n"
                    "- **Limit Node Count**: Target exactly 6-15 nodes total. Do NOT exceed 15 nodes.\n"
                    "- **Consolidate Aggressively**: If the repo has many services, group them into ONE node (e.g., 'Business Logic Services'). If there are multiple databases, use one node: 'Persistence Layer'.\n"
                    "- **Layer-to-Layer Connections**: Instead of connecting individual files, connect the containers. For example: `API_Layer --> Logic_Layer` rather than 10 separate arrows between controllers and services.\n\n"
                    "### SPATIAL ORGANIZATION:\n"
                    "- **Subgraphs as Tiers**: Create exactly 3-4 horizontal subgraphs: [External/Client], [API/Gateway], [Core Logic], [Infrastructure/Data].\n"
                    "- **Vertical Flow**: Ensure a strict top-to-bottom flow to keep the diagram linear and readable.\n"
                    "- **Connection Cleanup**: If two nodes have multiple interactions, use a single arrow with a generic label like 'Data Flow' or 'Internal API'.\n\n"
                    "### SYNTAX REFINEMENT:\n"
                    "- Use `Node[(Label)]` for databases and `Node{Label}` for decision points or gateways.\n"
                    "- Avoid cross-linking between subgraphs unless it is a primary system boundary.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate an executive-level `graph TD` diagram. {focus_instruction}\n"
                    "STRICT LIMIT: Max 15 nodes. Focus on the relationship between major layers, not individual components."
                ),
            },
        ]
    )

    raw = response.content or ""
    return _extract_mermaid_fence(raw)
