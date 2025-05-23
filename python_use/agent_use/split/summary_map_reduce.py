from langchain_community.document_loaders import TextLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
# 加载文档并分块
loader = TextLoader("./chineseJH.txt", encoding="utf-8")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
docs = loader.load_and_split(text_splitter)

# 初始化模型
llm = ChatOpenAI(model="qwen:7b", base_url="http://127.0.0.1:10087/v1", api_key="vllm")

# 创建链式处理器
chain = load_summarize_chain(
    llm,
    chain_type="refine",
    verbose=True,
    map_prompt=PromptTemplate.from_template("总结本段内容：\n{text}"),  # 自定义Map提示词
    combine_prompt=PromptTemplate.from_template("合并以下摘要：\n{text}") # 自定义Reduce提示词
)

# 执行总结（处理前5块）
result = chain.invoke(docs[:2])

print(result)
print("==="*50)
print(docs[:2])