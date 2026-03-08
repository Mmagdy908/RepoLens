from typing import Annotated

from langchain_core.tools import tool

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count
from langgraph.prebuilt import InjectedState


@tool
async def answer_general_question(
    question: str,
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Answer a general question about the repository."""
    _tools_usage_count["general_qa"] += 1
    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to answer the user's question accurately.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {"role": "user", "content": question},
        ],
    )
    return response.content or ""
