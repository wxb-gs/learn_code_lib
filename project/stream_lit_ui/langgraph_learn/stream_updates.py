from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

# 定义状态类（包含中间状态字段）


class State(dict):
    messages: list
    intermediate: str  # 新增字段用于流式中间结果


# 构建图
llm = ChatOllama(model="qwen2.5:7b", stream=True)  # 确保stream=True
builder = StateGraph(State)

# 改为流式节点函数


def llm_node(state: State):
    messages = state["messages"]

    # 流式调用LLM（核心改动）
    response_stream = llm.stream(messages)
    content = ""

    # 逐词生成并更新中间状态
    for chunk in response_stream:
        token = chunk.content
        content += token
        # 实时产出中间结果
        yield {"intermediate": content}

    # 最终更新完整消息
    yield {
        "messages": messages + [AIMessage(content=content)],
        "intermediate": ""  # 清空中间状态
    }


builder.add_node("llm_node", llm_node)
builder.set_entry_point("llm_node")
builder.set_finish_point("llm_node")
graph = builder.compile()

# 流式输出（使用updates模式获取增量变化）
for chunk in graph.stream(
    {"messages": [HumanMessage("如何学习Rag")], "intermediate": ""},
    stream_mode="updates"  # 改为updates模式更高效
):
    # 实时输出生成的token
    if "intermediate" in chunk.get("llm_node", {}):
        current = chunk["llm_node"]["intermediate"]
        # 计算新增内容（实现逐词效果）
        new_content = current[len(prev) if (
            prev := getattr(llm_node, 'last', '')) else 0:]
        print(new_content, end="", flush=True)
        llm_node.last = current  # 保存当前状态用于下次比对

    # 最终消息输出
    if "messages" in chunk.get("llm_node", {}):
        print("\n\n完整回复:", chunk["llm_node"]["messages"][-1].content)
