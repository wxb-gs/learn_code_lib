import uuid

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

@tool
def get_user_age(name: str) -> str:
    """Use this tool to find the user's age."""
    # This is a placeholder for the actual implementation
    if "bob" in name.lower():
        return "42 years old"
    return "41 years old"

memory = MemorySaver()
model = ChatOllama(model="Qwen2.5-7B-Instruct")

# 上下文处理得到
def prompt(state) -> list[BaseMessage]:
    """Given the agent state, return a list of messages for the chat model."""
    # We're using the message processor defined above.
    return trim_messages(
        state["messages"],
        token_counter=len,  # <-- len will simply count the number of messages rather than tokens
        max_tokens=5,  # <-- allow up to 5 messages.
        strategy="last",
        # Most chat models expect that chat history starts with either:
        # (1) a HumanMessage or
        # (2) a SystemMessage followed by a HumanMessage
        # start_on="human" makes sure we produce a valid chat history
        start_on="human",
        # Usually, we want to keep the SystemMessage
        # if it's present in the original history.
        # The SystemMessage has special instructions for the model.
        include_system=True,
        allow_partial=False,
    )

# 使用预定义的agent, 能够询问bob年龄的agent
app = create_react_agent(
    model,
    tools=[get_user_age],
    checkpointer=memory,
    prompt=prompt,
)

if __name__ == "__main__":
    # The thread id is a unique key that identifies
    # this particular conversation.
    # We'll just generate a random uuid here.
    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}

    # Tell the AI that our name is Bob, and ask it to use a tool to confirm
    # that it's capable of working like an agent.
    input_message = HumanMessage(content="hi! I'm bob. What is my age?")

    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        event["messages"][-1].pretty_print()

    # Confirm that the chat bot has access to previous conversation
    # and can respond to the user saying that the user's name is Bob.
    input_message = HumanMessage(content="do you remember my name?")

    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        event["messages"][-1].pretty_print()
