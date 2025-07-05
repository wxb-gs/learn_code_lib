from langchain.agents import AgentExecutor, Tool
from langchain.agents import create_tool_calling_agent
from langchain_ollama import ChatOllama
from langchain import hub

# 1. 初始化提示词
prompt = hub.pull("hwchase17/openai-functions-agent")

# 2. 初始化LLM
llm = ChatOllama(model="qwen2.5:7b")

# 3. 定义天气工具函数
def get_weather(location: str) -> str:
    """Get the weather in a given location."""
    return f"The weather in {location} is Sunny."

# 4. 封装为Tool对象
tools = [
    Tool(
        name="get_weather",
        func=get_weather,
        description="Get the current weather in a specified location"
    )
]

# 5. 创建Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 6. 初始化Executor（关键修改！）
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 启用详细日志
    handle_parsing_errors=True,  # 处理解析错误
    max_iterations=5,  # 防止无限循环[1,7](@ref)
    return_intermediate_steps=True  # 确保输出键存在[7](@ref)
)

# 7. 使用invoke代替run（关键修改！）
result = agent_executor.invoke(
    {"input": "San Francisco的天气如何呢?适合出去玩吗？"}
)
print(result["output"])  # 正确获取输出