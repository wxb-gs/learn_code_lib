from typing import TypedDict
from langgraph.graph import START, StateGraph
from langchain.chat_models import init_chat_model

from typing import TypedDict
from langgraph.types import StreamWriter
import asyncio


class State(TypedDict):
    topic: str
    joke: str


async def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Streaming custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}

graph = (
    StateGraph(State)
    .add_node(generate_joke)
    .add_edge(START, "generate_joke")
    .compile()
)


async def run():
    async for chunk in graph.astream(
        {"topic": "ice cream"},
        stream_mode="custom",
    ):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(run())
