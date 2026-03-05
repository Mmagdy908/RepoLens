from typing import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated
import operator


class AgentState(TypedDict):
    session_id: str
    repo_context: str
    messages: Annotated[list[AnyMessage], operator.add]
