from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count


@tool
async def get_tech_debt_summary(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Produce a technical debt summary for the repository.

    Identifies TODO/FIXME comments, deprecated patterns, missing tests,
    outdated dependencies, and other sources of accumulated debt.
    Returns a structured Markdown report with a prioritised action list.
    """
    _tools_usage_count["tech_debt"] += 1

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer performing a technical debt audit.\n"
                    "Analyse the repository and produce a structured Markdown report.\n\n"
                    "Use these sections:\n\n"
                    "## 📌 High-Priority Debt\n"
                    "Items that should be addressed in the next sprint to prevent escalating costs.\n\n"
                    "## ⚠️ Medium-Priority Debt\n"
                    "Items worth scheduling in the next quarter.\n\n"
                    "## 📝 Low-Priority / Housekeeping\n"
                    "Minor issues: stale TODOs, commented-out code, trivial naming inconsistencies.\n\n"
                    "## 🗺️ Recommended Refactoring Roadmap\n"
                    "A short ordered list (1–5 items) of concrete refactoring actions, most impactful first.\n\n"                    "Rules:\n"
                    "- Reference actual file paths and line-level evidence where possible.\n"
                    "- Do NOT fabricate issues absent from the code.\n"
                    "- Do NOT assume debt exists based on general knowledge — only report what the context confirms.\n"
                    "- If the context is insufficient to assess an area, say so rather than guessing.\n"
                    "- Use bullet points (`-`) within each section.\n"
                    "- If a section is empty, write `- None identified.`\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "Generate a technical debt summary for this repository.",
            },
        ]
    )

    return response.content
