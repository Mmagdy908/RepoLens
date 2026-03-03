import os
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool

from app.agent.nova_client import client

MODEL_ID = os.environ["NOVA_MODEL_ID"]


@tool
def get_project_overview(
    repo_context: Annotated[str, InjectedToolArg],
) -> str:
    """Return a high-level overview of the repository: purpose, main features, and structure."""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
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
        stream=False,
    )
    return response.choices[0].message.content or ""
