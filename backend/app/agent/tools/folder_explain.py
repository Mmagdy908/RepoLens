from typing import Annotated

from langchain_core.tools import tool

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count
from langgraph.prebuilt import InjectedState


@tool
async def get_folder_explanation(
    folder_path: str,
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Explain the purpose and contents of a specific folder in the repository."""
    _tools_usage_count["folder_explain"] += 1
    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to explain the requested folder: "
                    "its purpose, what files it contains, what responsibilities it owns, "
                    "and how it relates to the rest of the codebase.\n\n"
                    "Rules:\n"
                    "- Only describe files and responsibilities that are directly visible "
                    "in the repository context.\n"
                    "- Do NOT invent files, sub-folders, or responsibilities not present in the context.\n"
                    "- If the requested folder is not found in the context, say so explicitly "
                    "rather than guessing.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": f"Explain the folder: {folder_path}",
            },
        ],
    )
    return response.content or ""
