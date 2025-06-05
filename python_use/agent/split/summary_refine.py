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

# 修正后的提示模板
question_prompt = PromptTemplate(
    template="根据新内容完善总结：{text}",
    input_variables=["text"]
)

refine_prompt = PromptTemplate(
    template="当前总结：{existing_answer}\n新增内容：{text}\n生成更新后的总结：",
    input_variables=["existing_answer", "text"]
)

# 创建链式处理器
refine_chain = load_summarize_chain(
    llm,
    chain_type="refine",
    verbose=True,
    question_prompt=question_prompt,
    refine_prompt=refine_prompt
)

# 正确调用方式
inputs = {
    "input_documents": docs[:3],
    "question": "请总结以下内容"  # 自定义问题（可选）
}
refined_summary = refine_chain.invoke(inputs)
print(refined_summary)