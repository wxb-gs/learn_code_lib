import os
from mem0 import Memory
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate

llm = ChatOllama(model="qwen2.5:7b")

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1024  # 修改为实际模型维度
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5:7b",
            "temperature": 0,
            "max_tokens": 2000,
            "ollama_base_url": "http://localhost:11434",  # Ensure this URL is correct
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "bge-m3",
            
            # Alternatively, you can use "snowflake-arctic-embed:latest"
            "ollama_base_url": "http://localhost:11434",
        },
    },
}

# Initialize Memory with the configuration
m = Memory.from_config(config)
print("加载完成")
messages = [
    {"role": "user", "content": "Could you tell me what 1 plus 1111 equals?"},
    {"role": "assistant", "content": "1112"},
    {"role": "user", "content": "What is that answer plus 1?"},
    {"role": "assistant", "content": "1113"}
]
prompt = PromptTemplate(
    input_variables=["history", "question"],
    template = """
结合上述参考历史对话记录:{history}
回答:{question}"""
)


question = "最近的一个数学问题是什么"
myPrompt = prompt.format_prompt(
    history=messages,
    question=question
)
res = llm.invoke(myPrompt)
print(res.content)
messages.append({"role": "user", "content": question })
messages.append({"role": "assistant", "content": res.content})

# 确保 user_id 一致
m.add(messages, user_id="damn", metadata={"type": "math_qa"})


related_memories = m.search(query="waht's the last questions？", user_id="damn", filters={"type": "math_qa"})
print(related_memories )

