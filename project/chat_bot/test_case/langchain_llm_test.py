from langchain_openai import ChatOpenAI
from llama_index.llms.langchain import LangChainLLM

# 包装为llamaindex 风格的llm
llm = LangChainLLM(
    ChatOpenAI(
        model_name="qwen2.5:7b",
        base_url="http://localhost:8102/v1",
        api_key="vllm",
        temperature=0.7,
    )
)

response_gen = llm.stream_complete("你好, 如何学习Rag?")

for r in response_gen:
    print(r.delta, end="", flush=True)