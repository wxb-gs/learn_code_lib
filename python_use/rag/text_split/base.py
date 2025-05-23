from langchain_text_splitters import TokenTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

def split_documents(raw_documents, chunk_size=256, chunk_overlap=24):
    """使用文本分割器处理文档"""
    if not raw_documents:
        raise ValueError("没有可分割的文档内容")
    
    print("正在进行文档分割...")
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(raw_documents)
    
    print(f"已将文档页面分割成 {len(chunks)} 个片段。")
    return chunks

if __name__ == "__main__":
    # 注意编码格式， 默认的是gbk
    loader = TextLoader("./chineseJH.txt", encoding="utf-8")
    documents = loader.load()
    # 输出了文章全部内容
    print(documents[0])
    print(len(documents))
    print("===========================================================================================")

    chunks = split_documents(documents)