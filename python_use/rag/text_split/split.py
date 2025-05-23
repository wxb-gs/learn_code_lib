from langchain_text_splitters import RecursiveCharacterTextSplitter
from load_file import load_pdf_documents
import textwrap  # 用于文本格式化输出

# 增强版中文分块配置（支持中英文混合文档）
text_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",        # 空行（最高优先级）
        "。", "!", "?",  # 中文句末标点
        "\n",          # 换行符
        "；", ";",      # 分号
        " ", "",        # 空格和空字符（最低优先级）
    ],
    chunk_size=800,     # 增大块大小适应中文（约400-500汉字）
    chunk_overlap=150,  # 设置15%的重叠比例
    add_start_index=True,  # 记录分块起始位置
    is_separator_regex=False,
    strip_whitespace=False  # 保留原始空格格式
)

# 加载PDF文档（添加元数据增强）
raw_docs = load_pdf_documents("./pdfs")

print("\n" + "*" * 50 + " 原始文档信息 " + "*" * 50)
print(f"载入PDF文档数：{len(raw_docs)}")
print(f"首个文档元数据：{raw_docs[0].metadata}\n")

# 执行分块处理
chunks = text_splitter.split_documents(raw_docs)

print("\n" + "=" * 50 + " 分块统计信息 " + "=" * 50)
print(f"总块数：{len(chunks)}")
print(f"平均块长度：{sum(len(c.page_content) for c in chunks)//len(chunks)}字符")
print(f"最大块长度：{max(len(c.page_content) for c in chunks)}字符")
print(f"最小块长度：{min(len(c.page_content) for c in chunks)}字符\n")

# 详细分块信息输出
print("=" * 50 + " 分块详细信息 " + "=" * 50)
for i, chunk in enumerate(chunks[:3]):  # 示例显示前3个分块
    metadata = chunk.metadata
    content_preview = textwrap.shorten(
        chunk.page_content.strip(), 
        width=150, 
        placeholder="[...]"
    )
    
    print(f"""
▶ 块 {i+1}/{len(chunks)} 
├─ 源文件：{metadata.get('source', '未知')}
├─ 起始页：{metadata.get('page', 0)+1} 页
├─ 块位置：字符 {metadata['start_index']}-{metadata['start_index']+len(chunk.page_content)}
├─ 字符数：{len(chunk.page_content)}
└─ 内容预览：{content_preview}""")
    print("-" * 80)

# 打印分块分布直方图（可选）
if len(chunks) > 0:
    import matplotlib.pyplot as plt
    lengths = [len(c.page_content) for c in chunks]
    plt.hist(lengths, bins=20, edgecolor='black')
    plt.title("分块长度分布")
    plt.xlabel("char_number")
    plt.ylabel("chunks_number")
    plt.show()