from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

# 定义状态类（必须包含所有字段）


class State(dict):
    messages: list


# 构建图
llm = ChatOllama(model="qwen2.5:7b", stream=True)
builder = StateGraph(State)


def llm_node(state: State):
    response = llm.invoke(state["messages"])  # 非流式调用
    return {"messages": state["messages"] + [response]}


builder.add_node("llm_node", llm_node)
builder.set_entry_point("llm_node")
builder.set_finish_point("llm_node")
graph = builder.compile()

# 流式输出完整状态
for chunk in graph.stream(
    {"messages": [HumanMessage("如何学习Langgraph")]},
    stream_mode="messages"
):
    msg, _ = chunk
    print(msg.content)  # 每次输出最新消息
