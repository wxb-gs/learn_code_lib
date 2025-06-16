from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_ollama import ChatOllama
# ===== 1. 定义状态结构 =====


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "对话消息历史"]
    user_query: str

# ===== 2. 定义工具（模拟高风险API）=====


@tool
def search_weather_api(city: str) -> str:
    """调用外部天气API（模拟高风险操作）"""
    # 实际场景需替换为真实API调用
    print(f"⚠️ 模拟调用天气API: {city}")
    return f"{city}天气晴朗，25℃"

# ===== 3. 构建代理节点 =====


def agent_node(state: AgentState):
    """代理决策节点"""
    llm = ChatOllama(model="qwen2.5:7b")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ===== 4. 人工审核节点 =====


def human_approval_node(state: AgentState):
    """在调用API前暂停并等待人工确认"""
    last_msg = state["messages"][-1].content
    print(f"🔍 需人工审核的操作: {last_msg}")

    # 模拟人工输入（实际可替换为Web界面）
    approval = input("是否允许执行？(y/n): ").strip().lower()
    if approval == "y":
        print("✅ 操作已批准")
        return {"messages": [HumanMessage(content="继续执行")]}
    else:
        print("❌ 操作已拒绝")
        return {"messages": [HumanMessage(content="取消操作")]}


# ===== 5. 构建状态图 =====
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode([search_weather_api]))  # 工具调用节点
builder.add_node("human_approval", human_approval_node)     # 人工审核节点

# 设置边关系
builder.add_edge("agent", "human_approval")  # 代理决策后进入审核
builder.add_conditional_edges(
    "human_approval",
    lambda state: "tools" if "继续执行" in state["messages"][-1].content else "agent",
)  # 根据审核结果跳转
builder.add_edge("tools", "agent")           # 工具执行后返回代理
builder.add_edge("agent", END)              # 最终结束
builder.add_edge(START, "agent")
# 启用检查点（支持中断恢复）
checkpointer = MemorySaver()
config = {
    "thread_id": "123"
}
graph = builder.compile(checkpointer=checkpointer,
                        interrupt_before=["tools"])

# ===== 6. 执行代理 =====
if __name__ == "__main__":
    # 初始化输入
    inputs = {
        "messages": [HumanMessage(content="查询纽约天气")],
        "user_query": "纽约天气"
    }

    # 流式执行并打印过程
    print("🚀 开始执行代理流程...")
    for step in graph.stream(inputs, stream_mode="values", config=config):
        msg = step["messages"][-1]
        print(f"📢 {type(msg).__name__}: {msg.content}")
