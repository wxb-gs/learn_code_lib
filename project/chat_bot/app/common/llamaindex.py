import re
from llama_index.core import Settings
# embedding模型
from langchain_openai import ChatOpenAI
from llama_index.llms.langchain import LangChainLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# 索引及文件加载
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter, TokenTextSplitter, SentenceWindowNodeParser
from llama_index.core import Document


# 包装为llamaindex 风格的llm
llm = LangChainLLM(
    ChatOpenAI(
        model_name="qwen2.5:7b",
        base_url="http://localhost:8102/v1",
        api_key="vllm",
        temperature=0.4,
    )
)
Settings.llm = llm

# 设置嵌入模型
embed_model = HuggingFaceEmbedding(model_name="../models/bge-m3", device="cuda")
Settings.embed_model = embed_model

print("创建索引...")
# 默认的pdfreader都是一些乱码
pdf_reader = PyMuPDFReader()

loader = SimpleDirectoryReader(
   input_dir = "../data/docs/",
   required_exts=[".pdf", ".txt"],
   file_extractor={
       ".pdf": pdf_reader
   }
)
documents = loader.load_data()
print("文档加载完成")

def chinese_sentence_splitter(text):
    return [s for s in re.split(r"(?<=[。！？])", text) if s]

splitter = SentenceWindowNodeParser.from_defaults(
    # how many sentences on either side to capture
    window_size=3,
    # the metadata key that holds the window of surrounding sentences
    window_metadata_key="window",
    sentence_splitter=chinese_sentence_splitter
)
nodes = splitter.get_nodes_from_documents( documents= documents, show_progress=False)
index = VectorStoreIndex.from_documents(nodes, show_progress=True)

print("持久化存储索引...")
index.storage_context.persist("../data/storage")

query_engine = index.as_query_engine()
print(query_engine.retrieve("请问论文的作者和标题是什么的？"))
response = query_engine.query("请问论文的作者和标题是什么的？")
print(response)
