from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.agent.nova_client import client
from app.api.tools_usage import _tools_usage_count


@tool
async def get_security_concerns(
    repo_context: Annotated[str, InjectedState("repo_context")],
) -> str:
    """Audit the repository for security concerns and return a structured Markdown report.

    Covers hardcoded secrets, injection risks, insecure dependencies, missing
    auth/authz, improper error handling, and OWASP Top-10 relevant issues.
    """
    _tools_usage_count["security"] += 1

    response = await client.ainvoke(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert application security engineer performing a code audit.\n"
                    "Analyse the repository for security vulnerabilities and concerns.\n\n"
                    "Return a structured Markdown report with these sections:\n\n"
                    "## 🚨 Critical Vulnerabilities\n"
                    "Issues that could lead to data breach, RCE, or full compromise. Must be fixed immediately.\n\n"
                    "## 🔶 High-Risk Issues\n"
                    "Significant weaknesses that elevate attack surface (e.g. missing auth, unsafe deserialization).\n\n"
                    "## 🔷 Medium / Informational\n"
                    "Best-practice gaps, information leakage, insecure defaults, or hardening opportunities.\n\n"
                    "## ✅ Security Positives\n"
                    "Acknowledge secure patterns already in use.\n\n"
                    "## 🛡️ Recommended Mitigations\n"
                    "A short prioritised action list (most critical first).\n\n"
                    "Rules:\n"
                    "- Reference exact file paths, function names, and line-level evidence where possible.\n"
                    "- Do NOT invent vulnerabilities that aren't evidenced in the code.\n"
                    "- Map findings to OWASP Top-10 categories where applicable.\n"
                    "- Use bullet points (`-`) within each section.\n"
                    "- If a section is empty, write `- None identified.`\n\n"
                    f"<repo_context>\n{repo_context}\n</repo_context>"
                ),
            },
            {
                "role": "user",
                "content": "Perform a security audit of this repository and return the structured report.",
            },
        ]
    )

    return response.content
