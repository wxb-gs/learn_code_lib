from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict


@tool
def divide(a: float, b: float) -> int:
    """Return a / b."""
    return a / b


llm = ChatAnthropic(model="claude-3-haiku-20240307")
tools = [divide]


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.add_node("chatbot", lambda state: {
                       "messages": llm.bind_tools(tools).invoke(state['messages'])})
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_conditional_edges(
    "chatbot", tools_condition
)
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()
graph.invoke(
    {"messages": {"role": "user", "content": "What's 329993 divided by 13662?"}})
