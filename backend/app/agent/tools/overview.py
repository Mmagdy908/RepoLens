from typing import Annotated

from langchain_core.tools import tool

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count
from langgraph.prebuilt import InjectedState


@tool
async def get_project_overview(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Return a high-level overview of the repository: purpose, main features, and structure."""
    _tools_usage_count["overview"] += 1
    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to produce a concise, high-level overview "
                    "covering: what the project does, its main features, and how it is structured.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "Give me a high-level overview of this project.",
            },
        ],
    )

    return response.content or ""
