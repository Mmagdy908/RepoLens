import os
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool

from app.agent.nova_client import client

MODEL_ID = os.environ["NOVA_MODEL_ID"]


@tool
def get_file_explanation(
    file_path: str,
    repo_context: Annotated[str, InjectedToolArg],
) -> str:
    """Explain the purpose, responsibilities, and key logic of a specific file in the repository."""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to explain the requested file: "
                    "its purpose, responsibilities, key functions/classes, and how it fits "
                    "into the broader codebase.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": f"Explain the file: {file_path}",
            },
        ],
        stream=False,
    )
    return response.choices[0].message.content or ""
