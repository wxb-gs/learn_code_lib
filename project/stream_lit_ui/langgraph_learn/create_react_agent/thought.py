# 安装依赖
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, ToolMessage  # 新增导入
import asyncio
# 完整代码

# 1. 初始化支持工具调用的模型
model = ChatOllama(model="qwen2.5:7b")

# 2. 定义工具函数（带安全验证）


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息（仅支持北京/上海）"""
    if city not in ["北京", "上海"]:
        return "城市不在服务范围"
    # 模拟API调用（实际应替换为真实天气API）
    weather_data = {"北京": "晴，25℃", "上海": "多云，28℃"}
    return weather_data.get(city, "数据暂缺")


# 3. 创建工具集合并启用状态持久化
tools = [get_weather]
checkpointer = MemorySaver()  # 保存对话状态

# 4. 创建ReAct智能代理（带中断机制）
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer,
    prompt="""
don't need give the all (Thought/Action/Action Input/Observation), during the process you can give the part
Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""
)


# def run_agent(query: str, thread_id: str = "test_thread"):
#     config = {"configurable": {"thread_id": thread_id}}
#     inputs = {"messages": [("user", query)]}

#     # 流式输出执行过程
#     print(f"💡 [Question]{query}")
#     for msg, meta in agent.stream(inputs, stream_mode="messages", config=config):
#         # 获取当前步骤的消息列表
#         msg.pretty_print()
#         print("="*100)

async def run():
    config = {"configurable": {"thread_id": "123"}}
    inputs = {"messages": [("user", "北京和上海的天气分别如何？")]}
    async for event in agent.astream_events(inputs, config):
        print(event)
        print("=="*50)

if __name__ == "__main__":
    # run_agent("北京和上海的天气分别如何？")
    asyncio.run(run())
