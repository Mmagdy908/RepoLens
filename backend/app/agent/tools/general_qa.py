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
                "content": (                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to answer the user's question accurately.\n\n"
                    "Rules:\n"
                    "- Only assert facts that are directly evidenced in the repository context.\n"
                    "- Do NOT draw on general knowledge to fill gaps — if something is not in "
                    "the context, say explicitly that you cannot find it in the provided codebase.\n"
                    "- Do NOT invent file paths, function names, variable names, or library "
                    "versions that are not present in the context.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {"role": "user", "content": question},
        ],
    )
    return response.content or ""
