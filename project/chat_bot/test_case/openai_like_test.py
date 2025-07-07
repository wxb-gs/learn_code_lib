from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="qwen2.5:7b",
    temperature=0.7,
    api_base="http://127.0.0.1:8102/v1",
    api_key="vllm",
    is_chat_model=True
)

response_gen = llm.stream_complete("你好，如何学习Agent?")
for chunk in response_gen:
    print(chunk.delta, end="", flush=True)