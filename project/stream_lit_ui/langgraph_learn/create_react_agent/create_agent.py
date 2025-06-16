import pprint
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver


def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"


model = ChatOllama(model="qwen2.5:7b")
tools = [check_weather]

# 1. 创建代理
agent = create_react_agent(model, tools, checkpointer=MemorySaver())

# 2. 定义流式输出处理函数


def print_stream(stream):
    for step in stream:
        messages = step.get("messages", [])
        for msg in messages:
            print(f"📝 [Message] {msg}")


config = {
    "thread_id": "123"
}
# 3. 执行并输出全过程
inputs = {"messages": [("user", "查询纽约天气")]}
print_stream(agent.stream(inputs, stream_mode="values", config=config))
history = agent.get_state_history(config=config)
for state in history:
    print(f"Step: {state}, Next: {state}")
