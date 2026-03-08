from typing import Annotated

from langchain_core.tools import tool

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count
from langgraph.prebuilt import InjectedState


@tool
async def get_tech_stack(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Identify and list the technology stack used in the repository."""
    _tools_usage_count["tech_stack"] += 1
    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to identify the full technology stack: "
                    "languages, frameworks, libraries, databases, infrastructure, and tooling. "
                    "Present the result as a structured markdown list grouped by category.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "What is the technology stack of this project?",
            },
        ],
    )
    return response.content or ""
