# 步骤1：导入模块
from llama_index.core.extractors import TitleExtractor, SummaryExtractor
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage

from pprint import pprint
from datetime import datetime
from pydantic import BaseModel, Field


# 定义Pydantic数据模型
class Response(BaseModel):
    """The Response of the question"""
    answer: int = Field(
        description="The answer of the math calculation"
    )

custom_llm = Ollama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",  # 明确指定本地地址
    request_timeout=60.0  # 延长超时时间
)

structured_llm = custom_llm.as_structured_llm(Response)
res = structured_llm.chat(messages=[ChatMessage(content="计算12+33=?")])
pprint(res.raw)