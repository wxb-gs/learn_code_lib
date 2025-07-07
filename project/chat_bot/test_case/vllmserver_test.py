from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.vllm import VllmServer
# 配置 vLLM 服务端点
llm = VllmServer(
    model="qwen2.5:7b",
    api_url="http://localhost:8102/v1",
    max_new_tokens=1024,
    temperature=0.7
)

for chunk in  llm.stream_complete("你好, 如何学习Rag?"):
    print(chunk)

# 需要torch
