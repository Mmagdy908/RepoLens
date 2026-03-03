import os
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool

from app.agent.nova_client import client

MODEL_ID = os.environ["NOVA_MODEL_ID"]


@tool
def get_architecture_summary(
    repo_context: Annotated[str, InjectedToolArg],
) -> str:
    """Summarise the high-level architecture of the repository."""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer analysing a code repository. "
                    "Use the repository context below to describe the high-level architecture: "
                    "major components, how they interact, data flow, and key design decisions. "
                    "Present the result as a clear, structured markdown document.\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "Describe the architecture of this project.",
            },
        ],
        stream=False,
    )
    return response.choices[0].message.content or ""
