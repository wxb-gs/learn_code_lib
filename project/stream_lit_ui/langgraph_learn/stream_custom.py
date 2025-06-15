from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START
from langgraph.config import get_stream_writer
from langchain_core.messages import HumanMessage
# 定义状态类（必须包含所有字段）


class State(dict):
    messages: list


llm = ChatOllama(model="qwen2.5:7b", stream=True)
builder = StateGraph(State)


def llm_node(state: State):
    writer = get_stream_writer()
    writer({"value": 30})  # 自定义事件
    response = llm.invoke(state["messages"])
    writer({"value": 100})
    return {"messages": state["messages"] + [response]}


builder.add_node("llm_node", llm_node)
builder.set_entry_point("llm_node")
builder.set_finish_point("llm_node")
graph = builder.compile()


# 流式接收自定义事件
for chunk in graph.stream(
    {"messages": [HumanMessage(content="如何学习Rag?")]},
    stream_mode="custom"
):
    print(chunk)
