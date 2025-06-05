from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    HumanMessage
)

# 初始化 LLM
llm = ChatOllama(model="qwen2.5:7b")

# 定义图状态：只包含消息列表
class GraphState(dict):
    pass

# 节点1：调用 LLM
def answer_question(state: GraphState) -> GraphState:
    messages = state["messages"]
    response = llm(messages)
    state["messages"].append({"role": "assistant", "content": response.content})
    return state

# 1. 判断是否需要搜索
def should_search(state: GraphState) -> str:
    question = state["messages"][-1]["content"]
    if "latest" in question or "current" in question:
        return "search"
    return "answer"

# 2. 定义搜索节点
def search_web(state: GraphState) -> GraphState:
    # 假设是搜索后的结果
    result = "According to recent sources, ..."
    state["messages"].append({"role": "function", "name": "search_web", "content": result})
    return state

# 构建图
graph = StateGraph(GraphState)

# 添加节点
graph.add_node("answer", answer_question)
graph.add_node("search", search_web)

# 添加分支判断
graph.add_conditional_edges("router", should_search, {
    "answer": "answer",
    "search": "search",
})

# 路由后进入终点
graph.add_edge("answer", END)
graph.add_edge("search", END)

graph.set_entry_point("router")

app = graph.compile()

# 测试
state = GraphState(messages=[HumanMessage(content="What is the latest news about AI?")])
result = app.invoke(state)
print(result["messages"][-1]["content"])
