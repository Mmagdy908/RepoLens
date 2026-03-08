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
async def generate_component_diagram(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Generate a Mermaid component graph showing the major modules/packages
    of the repository and their dependencies."""
    _tools_usage_count["diagram_component"] += 1

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (                    "You are an expert software architect analysing a code repository.\n"
                    "Your ONLY output must be a single Mermaid fenced code block using `graph TD` or `graph LR`.\n"
                    "Do NOT include any prose, headings, or explanation — just the fence.\n\n"
                    "Diagram rules:\n"
                    "- Show modules/packages as nodes; edges represent imports or dependencies\n"
                    "- Group nodes into `subgraph` blocks that mirror the actual directory structure\n"
                    "- Use `classDef` + `class` to colour-code node types — "
                    "choose the colours yourself so they look professional and are easy to read\n"
                    "- Add edge labels where the relationship type is non-obvious "
                    "(e.g. `-->|imports|`, `-->|extends|`)\n"
                    "- Omit standard-library and third-party packages unless architecturally significant\n"
                    "- Keep node labels concise (module or package name only)\n"
                    "- Accurately reflect the actual code structure\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Generate a Mermaid component diagram showing the major modules "
                    "and their dependency relationships in this project."
                ),
            },
        ],
    )

    raw = response.content or ""
    return _extract_mermaid_fence(raw)
