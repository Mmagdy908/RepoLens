from typing import Annotated

from langchain_core.tools import tool

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count
from langgraph.prebuilt import InjectedState


@tool
async def get_architecture_summary(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Summarise the high-level architecture of the repository."""
    _tools_usage_count["architecture"] += 1
    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to describe the high-level architecture: "
                    "major components, how they interact, data flow, and key design decisions. "
                    "Present the result as a clear, structured markdown document.\n\n"
                    "Rules:\n"
                    "- Only describe components, interactions, and design decisions that are "
                    "directly evidenced in the repository context.\n"
                    "- Do NOT invent components, layers, or patterns that are not visible in the code.\n"
                    "- Do NOT assume standard architectural patterns apply unless the code confirms them.\n"
                    "- If the context is insufficient to describe a part of the architecture, "
                    "say so explicitly rather than guessing.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "Describe the architecture of this project.",
            },
        ],
    )
    return response.content or ""
