from langchain_openai import ChatOpenAI
from langchain_community.tools import BraveSearch
from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langgraph.prebuilt import ToolNode
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_amazon_nova import ChatAmazonNova

load_dotenv()


# Define a state class to track conversation history
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# Initialize a search tool to enhance the agent's abilities
def search_tool(query: str) -> str:
    """
    A tool for performing a web search.
    """
    return f"Search results for '{query}': [Result 1, Result 2, Result 3]"


tools = [search_tool]

# Set up the language model
llm = ChatAmazonNova(
    model=os.environ["NOVA_MODEL_ID"],
    api_key=os.environ["NOVA_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools=tools)


# Define the main language model node.
# This function takes the current conversation state,
# passes all previous messages to the language model (with tools bound),
# and returns the response as the new list of messages.
def model(state: AgentState):
    return {
        "messages": [llm_with_tools.invoke(state["messages"])],
    }


# Define the router node to determine the next step in the conversation.
# If the model's last message includes a tool call (e.g., a search request),
# we route to the tool node. Otherwise, we end the cycle.
def tools_router(state: AgentState):
    last_message = state["messages"][-1]

    # Check if the last message includes any tool calls
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tool_node"  # Route to the tool node to process the request
    else:
        return END  # End the conversation loop if no tool is needed


# Create a tool node for invoking external tools (e.g., BraveSearch)
tool_node = ToolNode(tools=tools)

# Initialize the state graph with our AgentState definition
graph = StateGraph(AgentState)

# Add the language model and tool nodes to the graph
graph.add_node("model", model)
graph.add_node("tool_node", tool_node)

# Set the model node as the entry point; all conversations start here
graph.set_entry_point("model")

# Add a conditional edge:
# After the model runs, use tools_router to decide the next step
graph.add_conditional_edges("model", tools_router)

# If a tool is used, return to the model node for follow-up
graph.add_edge("tool_node", "model")

# Compile the state graph into an executable application
compiled_graph = graph.compile()


# from openai import AsyncOpenAI

# from langchain_google_genai import ChatGoogleGenerativeAI
# from google import genai


app = FastAPI()

# client = genai.Client(
#     api_key="AIzaSyC-0-cgtX49_1JyGLIvK1FQSpFo4ZwqopU",
# )


async def event_stream(prompt_text: str):
    input = {"messages": ["Hi, How are you?"]}

    events = compiled_graph.astream_events(input=input, version="v2")

    async for event in events:
        # print(event)
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"].get("chunk").content
            if chunk:
                print(f"data:{chunk}\n\n")
                yield f"data:{chunk}\n\n"


# async def event_stream(prompt_text: str):
#     stream = client.models.generate_content_stream(
#         model="gemini-3.1-flash-lite-preview",
#         contents=prompt_text,
#     )
#     for chunk in stream:
#         token = chunk.text or ""
#         if token:
#             yield f"data: {token}\n\n"


@app.get("/stream")
async def stream_response(prompt: str):
    return StreamingResponse(event_stream(prompt), media_type="text/event-stream")
