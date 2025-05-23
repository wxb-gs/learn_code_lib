from .load_file import load_pdf_documents

CHROMA_KEY = "langchain"


def build(self, folder):
    try:
        new_docs = load_pdf_documents(folder)
        vector_store = self.client.get_or_create_collection(
            name=CHROMA_KEY, embedding_function=self.embedding
        )
        vector_store.add(
            documents=[doc.page_content for doc in new_docs],
            metadatas=[doc.metadata for doc in new_docs],
            ids=[f"doc_{i}" for i in range(len(new_docs))],
        )
        print("文档，向量模型构造完成")
    except Exception as e:
        print(f"错误：设置向量索引时出错: {e}")
        print("向量搜索功能可能受影响。")