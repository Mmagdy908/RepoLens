from typing import TypedDict


class AgentState(TypedDict):
    session_id: str
    repo_context: str
    messages: list[dict]
