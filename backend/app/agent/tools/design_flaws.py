from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count


@tool
async def find_design_flaws(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Analyse the repository for design flaws and return a structured markdown report.

    The report uses 🔴 (critical), 🟡 (warning), and 🟢 (good) sections to
    categorise findings by severity.
    """
    _tools_usage_count["design_flaws"] += 1

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are a senior software architect performing a design review.\n"
                    "Analyse the repository for design flaws, anti-patterns, and architectural issues.\n\n"
                    "Return a structured Markdown report with exactly these three sections:\n\n"
                    "## 🔴 Critical Issues\n"
                    "List serious design flaws that will cause maintainability, scalability, or correctness problems.\n"
                    "Each item: `**Issue title** — explanation and affected file(s)/module(s).`\n\n"
                    "## 🟡 Warnings\n"
                    "List notable code smells, questionable design choices, or coupling concerns.\n"
                    "Each item: `**Issue title** — explanation and affected file(s)/module(s).`\n\n"
                    "## 🟢 Strengths\n"
                    "Acknowledge well-designed areas so the report is balanced.\n"
                    "Each item: `**Strength title** — brief explanation.`\n\n"
                    "Rules:\n"
                    "- Be specific: reference actual file paths, class names, and function names from the repo.\n"
                    "- Do NOT invent issues that aren't evidenced in the code.\n"
                    "- Use bullet points (`-`) for each item within a section.\n"
                    "- If a section is empty, write `- None identified.`\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Analyse this repository for design flaws and return the structured 🔴/🟡/🟢 report."
                ),
            },
        ]
    )

    return response.content
