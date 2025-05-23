import os
from langchain_openai import ChatOpenAI
from mem0 import Memory

### 设置环境
os.environ["OPENAI_API_KEY"] =  'sk-d58877221cec4f208dc353259ca9c8bc' # 阿里云Qwen密钥
os.environ["OPENAI_BASE_URL"] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'   # 例如：https://dashscope.aliyuncs.com/compatible-mode/v1


# 初始化大模型
llm = ChatOpenAI(
    # model=os.getenv('DEEPSEEK_MODEL'),
    # api_key=os.getenv('DEEPSEEK_API_KEY'),
    # base_url=os.getenv('DEEPSEEK_URL')
    model = "qwen-plus",
    api_key =  os.getenv('OPENAI_API_KEY'),
    base_url = os.getenv('OPENAI_BASE_URL')
)

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768,  # Change this according to your local model's dimensions
        },
    },
    "llm": {
        "provider": "openai",  # 原值为"ollama"
        "config": {
            "model": "qwen-plus",  # 指定阿里云模型名称
            "api_key": os.getenv('OPENAI_API_KEY'),  # 使用环境变量中的密钥
            "base_url": os.getenv('OPENAI_BASE_URL')  # 阿里云API端点
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text:latest",
            # Alternatively, you can use "snowflake-arctic-embed:latest"
            "ollama_base_url": "http://localhost:11434",
        },
    },
}

# Initialize Memory with the configuration
m = Memory.from_config(config)

# Add a memory
m.add("I'm visiting Paris", user_id="john")

# Retrieve memories
memories = m.get_all(user_id="john")