# —— 一.屏蔽 Neo4j 驱动服务器通知 —— 
import logging
logging.getLogger("neo4j.notifications").setLevel(logging.CRITICAL)
logging.getLogger("neo4j.bolt").setLevel(logging.CRITICAL)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

import os
from typing import List, Tuple
from pydantic import BaseModel, Field

from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from langchain_neo4j import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker


# —— 二.环境变量 —— 
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "12345678"


# graph = Neo4jGraph(
#         url="bolt://localhost:7687",
#         username="neo4j",
#         password="password",
#         database="neo4j",
#         timeout=60  # 60 seconds timeout
#     )


# —— 三.初始化 Neo4jGraph —— 
# driver_config 可继续保持关闭通知的配置
graph = Neo4jGraph(
    url=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USERNAME"],
    password=os.environ["NEO4J_PASSWORD"],
    driver_config={"notifications_min_severity": "OFF"}
)

# —— 四.RAG 的混合检索 ——  
# 4.1 非结构化数据检索（向量检索，使用 bge-m3 嵌入）
embedding_model = OllamaEmbeddings(
    model="bge-m3:latest",
    base_url="http://localhost:11434/"  # 同上
)

llm = ChatOllama(
    model="Qwen2.5-7B-Instruct:latest",
    temperature=0.5,
    base_url="http://localhost:11434/"  # 同上
)

vector_index = Neo4jVector.from_existing_graph(
    embedding_model,
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
)

# 4.2 图检索器
graph.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")

# —— 实体提取 ——  
class Entities(BaseModel):
    names: List[str] = Field(..., description="ENTITY LIST")

entity_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are extracting organization and person entities from the text."),
    ("human", """Use the given format to extract Entity from the following input: {question}
     
                Group the extracted terms into the following three categories:
     
                1. [Proper Nouns]: Well-known or standard proper names, such as countries, weapons, military organizations, famous individuals, etc.
                2. [Military-Related Entities]: Any military terminology, equipment names, ranks, branches of the armed forces, battle names, military bases, treaties, or operations.
                3. [Unrecognized but Possibly Entities]: Terms that the model may not fully recognize but appear to be named entities, such as acronyms, foreign terms, or unfamiliar designations.
"""),
])

entity_chain = entity_prompt | llm.with_structured_output(Entities)

def generate_full_text_query(text: str) -> str:
    tokens = [tok for tok in remove_lucene_chars(text).split() if tok]
    return " ".join(f"{tok}~2" for tok in tokens)

# —— 结构化检索 ——  
def structured_retriever(question: str) -> str:
    result = []
    entities = entity_chain.invoke({"question": question}).names
    for ent in entities:
        # 1. 生成 lucene 查询，并跳过空查询
        lucene_q = generate_full_text_query(ent)
        if not lucene_q.strip():
            # 没跑出任何 token，就跳过
            continue

        # 2. 执行带作用域的子查询
        try:
            records = graph.query(
                """
                CALL db.index.fulltext.queryNodes('entity', $query, {limit: 2})
                YIELD node, score
                CALL (node) {
                  MATCH (node)-[r:MENTIONS]->(nbr)
                  RETURN node.id + ' - ' + type(r) + ' -> ' + nbr.id AS output
                  UNION ALL
                  MATCH (node)<-[r:MENTIONS]-(nbr)
                  RETURN nbr.id + ' - ' + type(r) + ' -> ' + node.id AS output
                }
                RETURN output
                LIMIT 50
                """,
                {"query": lucene_q},
            )
        except Exception as e:
            # 如果还有别的奇怪错误，也直接跳过这个实体
            continue

        result.extend(rec["output"] for rec in records)

    return "\n".join(result)





#定义rag链

chat_prompt = ChatPromptTemplate.from_template(
    """
    请严格按照以下指南回答用户问题：

    ！！！只能使用中文回答


    1. **仔细分析问题**，识别其中的**关键词**和**核心概念**。
    2. **从上下文中精确定位**相关信息，优先使用**完全匹配**的内容。
    3. 构建回答时，确保**包含所有必要的关键词**。
    4. 保持回答与原文的**语义相似度**。
    5. 如果上下文信息**不足以回答问题**，请直接说明“**根据提供的信息无法回答该问题**”。
    6. 如果问题涉及**数字、日期或具体数据**，务必在回答中**准确包含这些信息**。
    7. 回答应**准确、完整**，直接解答问题。
    8. 不要输出“检索到的文本块”“根据”等**前缀修饰句**，直接输出答案即可。
    
    ...

    **目标**：提供一个既准确又全面的回答，以获得最高的评分。

    **问题**：{query}

    **参考上下文**：
    ···
    {chat_history}
    {context}
    ···
    """
)




# —— 增加追问检测 ——
follow_up_keywords = [
        "扩充", "详细", "补充", "具体", "进一步", "更多", 
        "上一个", "刚才", "之前", "这个问题", "该问题",
        "详细说明", "进一步说明", "更详细", "更具体",
        "展开", "深入", "继续", "再说", "说说",
        "expand", "detail", "elaborate", "more", "further"
]

class ChatBot():
    def __init__(self):
        self.llm = llm
        self.memory = ConversationSummaryMemory(
            llm = self.llm
        )

        self.chain = (
            {
                "context": self.retriever,
                "chat_history": self.memory.load_memory_variables,
                "query": RunnablePassthrough(),
            }
            | chat_prompt
            | self.llm
            | StrOutputParser()
        )

        self.source_list = []    #当前来源文件列表
        self.page_list = []  #当前来源文件对应的页码列表
        self.last_source = []    #上一个问题的来源文件列表
        self.last_page = []  #上一个问题的来源文件对应的页码列表

    def get_source_page(self,question):
        refs_text = "\n"
        judge = 1
        for item in follow_up_keywords:
            if item in question:
                judge = 0
                for i in range(len(self.last_source)):
                    refs_text += f"- {self.last_source[i]}, 页码: {self.last_page[i]}\n"
                break
        if judge == 1:
            for i in range(len(self.source_list)):
                refs_text += f"- {self.source_list[i]}, 页码: {self.page_list[i]}\n"
        return refs_text

    def retriever(self,question: str) -> tuple[str, list[tuple[str, str]]]:
        # struct = structured_retriever(question)
        struct = ""
        unstruct_docs = vector_index.similarity_search(question, k=3)
        # print(unstruct_docs)

        text_chunks = []

        for doc in unstruct_docs:
            text = doc.page_content.strip()
            meta = doc.metadata
            source = os.path.basename(meta.get("source", "未知来源"))
            page_label = meta.get("page_label", "未知页码")
            if source in self.source_list and page_label in self.page_list :
                continue
            else:
                self.source_list.append(source)
                self.page_list.append(page_label)
            text_chunks.append(text)

        self.last_source = self.source_list
        self.last_page = self.page_list
        unstruct = "\n\n".join(text_chunks)
        all_context = f"\n{struct}\n\n{unstruct}"
        # print(all_context)
        return all_context

    def answer(self,question):

        res = self.chain.invoke(question)

        source = self.get_source_page(question)

        self.memory.save_context({"input": question}, {"output": res})

        final_output = f"{res}\n\n"

        self.source_list = []
        self.page_list = []

        return final_output,source


# —— 六.测试 RAG ——  
if __name__ == "__main__":
    print("测试开始...")


    #MATCH ()-[r]->(n:Document{id: "d3732f3bfa8d832b8be8679a99160f62"}) return r

    #Passive AMD entails the following types of actions:？
    #activities in support of the overall FP effort for the joint force:？
    #What about Joint Center for Electromagnetic Readiness (JCER).？
    #What about JEMSO Cells (JEMSOCs)？
    #What about Common Human-Machine Teaming Constructs？
    #Medical support in the joint environment is a key component of expeditionary and operational planning. The following Air Force medical capabilities are provided to the joint force commander:？
    #The air component commander should ensure the following authorities are defined to ensure clear lines of control during multirole missions:？
    #The following types of missions are most closely associated with active AMD:?

    questions = [
        "Examples of EMSO activities in support of CO include:?"
    ]
    chatbot = ChatBot()

    # print("********************")
    # records = graph.query(
    #             """
    #             MATCH (n:Document {id: "4fb22f4558b8f288cbaf51ca72fb574b"}) RETURN n LIMIT 5
    #             """
    #         )
    # records = graph.query(
    #             """
    #             MATCH (n:Document{id: "4fb22f4558b8f288cbaf51ca72fb574b"})-[r]->() return r
    #             """
    #         )
    # for item in records:
    #     print("*******************")
    #     print(item['n'].get('text'))
    #     print("\n")

    for question in questions:
        print("\n问题:", question)

        res = chatbot.answer(question)

        print(res)
        print("-" * 50)

    print("测试结束。")





