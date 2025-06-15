from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent


def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"


agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b"),
    tools=[check_weather],
)

# 默认react_agent中使用invoke同步调用大模型，如果希望流式输出token by token使用messages
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "今天的北京的天气如何？回答如何学习Rag"}]},
    stream_mode=["updates", "custom"]
):
    print(chunk)
    print("="*100)

# res = agent.invoke(
#     {"messages": [{"role": "user", "content": "今天的北京的天气如何？回答如何学习Rag"}]})
# print(res)
