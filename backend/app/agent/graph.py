import os
from langchain_core.messages import BaseMessage
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.tools.architecture import get_architecture_summary
from app.agent.tools.file_explain import get_file_explanation
from app.agent.tools.folder_explain import get_folder_explanation
from app.agent.tools.general_qa import answer_general_question
from app.agent.tools.overview import get_project_overview
from app.agent.tools.tech_stack import get_tech_stack
from app.agent.tools.diagram_architecture import generate_architecture_diagram
from app.agent.tools.diagram_sequence import generate_sequence_diagram
from app.agent.tools.diagram_component import generate_component_diagram
from langchain_amazon_nova import ChatAmazonNova

_llm = ChatAmazonNova(
    model=os.environ["NOVA_MODEL_ID"],
    api_key=os.environ["NOVA_API_KEY"],
    streaming=True,  # Enable streaming responses
)

ALL_TOOLS = [
    answer_general_question,
    get_project_overview,
    get_tech_stack,
    get_architecture_summary,
    get_file_explanation,
    get_folder_explanation,
    generate_architecture_diagram,
    generate_sequence_diagram,
    generate_component_diagram,
]

_llm_with_tools = _llm.bind_tools(ALL_TOOLS)

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


async def agent_node(state: AgentState) -> dict:
    """Call the LLM with the current message history and return the AI reply.
    response is added to current messages because of Annotated[list[AnyMessage], operator.add]"""
    response: BaseMessage = await _llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}


# ToolNode automatically executes whichever tool the LLM selected.
# InjectedToolArg fields are injected from the graph state automatically.
tool_node = ToolNode(
    tools=ALL_TOOLS,
    # Pass state fields that are marked InjectedToolArg
    handle_tool_errors=True,
)

# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

_builder = StateGraph(AgentState)

_builder.add_node("agent", agent_node)
_builder.add_node("tools", tool_node)

_builder.add_edge(START, "agent")

# tools_condition returns "tools" if the last message has tool_calls, else END
_builder.add_conditional_edges(
    "agent",
    tools_condition,
    ["tools", END],
)

# After tool execution always return to the agent node
_builder.add_edge("tools", "agent")

compiled_graph = _builder.compile()
