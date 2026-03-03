import os

from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool

from app.agent.nova_client import client

MODEL_ID = os.environ["NOVA_MODEL_ID"]


@tool
def answer_general_question(
    question: str,
    repo_context: Annotated[str, InjectedToolArg],
) -> str:
    """Answer a general question about the repository."""
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
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
        stream=False,
    )
    return response.choices[0].message.content or ""
