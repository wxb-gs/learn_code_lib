import glob
import os
from langchain_community.document_loaders import PyPDFLoader

def load_pdf_documents(pdf_folder):
    """从指定文件夹加载PDF文档"""
    raw_documents = []
    
    if not os.path.isdir(pdf_folder):
        raise FileNotFoundError(f"指定的 PDF 文件夹不存在: {pdf_folder}")
    
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"), recursive=True)
    if not pdf_files:
        print(f"警告：在文件夹 {pdf_folder} 中未找到 PDF 文件。")
        return []
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件。正在加载...")
    for pdf_path in pdf_files:
        try:
            print(f"  加载中: {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            pdf_pages = loader.load()
            raw_documents.extend(pdf_pages)
            print(f"  加载了 {len(pdf_pages)} 页.")
        except Exception as pdf_error:
            print(f"  错误：加载 PDF 文件失败: {pdf_path}. 错误: {pdf_error}")
    return raw_documents

if __name__ == "__main__":
    raw_documents = load_pdf_documents("./pdfs")
    print(raw_documents[0])