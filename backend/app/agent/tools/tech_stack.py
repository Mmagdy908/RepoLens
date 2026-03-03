import os
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool

from app.agent.nova_client import client

MODEL_ID = os.environ["NOVA_MODEL_ID"]


@tool
def get_tech_stack(
    repo_context: Annotated[str, InjectedToolArg],
) -> str:
    """Identify and list the technology stack used in the repository."""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
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
        stream=False,
    )
    return response.choices[0].message.content or ""
