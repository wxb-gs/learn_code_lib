from langgraph.types import StreamWriter
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
import asyncio
from langgraph.config import get_stream_writer
# 初始化 LLM 和工具
llm = ChatOllama(model="qwen2.5:7b")

# 自定义工具节点（集成流式输出）


def get_weather_tool(city: str) -> str:
    """获取city的天气

    Args:
        city (str): 城市

    Returns:
        str: 天气结果
    """
    # writer = get_stream_writer()
    # writer.send("tool_progress", {"message": f"查询{city}天气中..."})  # 发送进度事件
    weather_data = "fetch_weather_api(city) "  # 调用真实 API
    # writer.send("tool_result", {"data": weather_data})  # 发送结果事件
    return weather_data


tools = [get_weather_tool]  # 假设已定义天气查询工具

# 创建 React Agent
agent = create_react_agent(llm, tools)


async def run_agent():
    inputs = {"messages": [{"role": "user", "content": "如何学习Rag?"}]}
    # agent.stream(input=inputs, stream_mode=["messages", "custom"])
    # ans = agent.invoke(inputs)
    # print(ans)

    async for event in agent.astream_events(
        inputs,
        version="v2"           # 使用事件流 API
    ):
        event_type = event["event"]
        data = event["data"]
        # if event_type == "on_chat_model_stream":
        #     print(data)
        #     print("="*100)
        # print(event)

        # if event_type == "on_tool_start":
        #     print(f"🛠️ 调用工具: {data['tool_name']}")

        # elif event_type == "tool_progress":  # 处理自定义工具事件
        #     print(f"⏳ {data['message']}")

        # elif event_type == "tool_result":
        # #     print(f"✅ 查询结果: {data['data']}")

        # elif event_type == "on_chat_model_stream":  # LLM Token 流
        #     print(data["chunk"].content, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run_agent())
