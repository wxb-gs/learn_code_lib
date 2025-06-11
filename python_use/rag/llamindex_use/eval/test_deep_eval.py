import pytest
import logging
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval import assert_test
from llama_index.core import StorageContext, load_index_from_storage
from deepeval.models.llms.ollama_model import OllamaModel
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import AnswerRelevancyMetric

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# 设置 LLM 模型（如 llama3.1）
Settings.llm = Ollama(model="qwen2.5:7b", request_timeout=360.0)

# 设置嵌入模型（如 nomic-embed-text）
Settings.embed_model = OllamaEmbedding(model_name="bge-m3")

storage_context = StorageContext.from_defaults(persist_dir="storage")
index = load_index_from_storage(
    storage_context,
    # we can optionally override the embed_model here
    # it's important to use the same embed_model as the one used to build the index
)
eval_model = OllamaModel(model="qwen2.5:32b")

dataset = EvaluationDataset()
dataset.pull(alias="af")


rag_chat = index.as_chat_engine()
def your_llm_app(input: str):
    response = ""
    streaming_response = rag_chat.stream_chat(input)
    for token in streaming_response.response_gen:  # 正确访问响应生成器[2](@ref)
        print(token, end="", flush=True)  # 实时输出
        response += token
    return response


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("evaluation.log"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

@pytest.mark.parametrize("golden", dataset.goldens)
def test_llm_app(golden: Golden):
    logging.info(f"🚀 开始测试用例: {golden.input}")
    
    # 执行LLM调用
    response = your_llm_app(golden.input)  
    logging.info(f"✅ LLM响应: {response[:100]}...")  # 记录前100字符
    
    test_case = LLMTestCase(
        input=golden.input, 
        actual_output=response
    )
    
    # 执行评估
    metric = AnswerRelevancyMetric(model=eval_model)
    metric.measure(test_case)
    logging.info(f"📊 评估得分: {metric.score} | 原因: {metric.reason}")
    
    assert_test(test_case=test_case, metrics=[metric])
    logging.info("✅ 测试完成\n" + "-"*50)

