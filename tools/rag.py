from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import os

# 全局变量存储向量数据库
_vector_store = None

def initialize_rag():
    """初始化RAG向量数据库"""
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    # 读取知识库文件
    knowledge_dir = "knowledge"
    documents = []

    for filename in ["faq.txt", "rules.txt", "cases.txt"]:
        filepath = os.path.join(knowledge_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append({"content": content, "source": filename})

    # 文本分割
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=500,
        chunk_overlap=50
    )

    texts = []
    metadatas = []
    for doc in documents:
        chunks = text_splitter.split_text(doc["content"])
        texts.extend(chunks)
        metadatas.extend([{"source": doc["source"]}] * len(chunks))

    # 创建向量数据库
    embeddings = OpenAIEmbeddings()
    _vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    return _vector_store

@tool
def rag_search(query: str, top_k: int = 3) -> str:
    """
    在知识库中检索相关信息。

    参数:
        query: 检索查询
        top_k: 返回结果数量

    返回:
        检索到的相关知识内容
    """
    try:
        vector_store = initialize_rag()
        results = vector_store.similarity_search(query, k=top_k)

        if not results:
            return "未找到相关知识"

        output = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "未知来源")
            output.append(f"[来源: {source}]\n{doc.page_content}")

        return "\n\n---\n\n".join(output)

    except Exception as e:
        return f"检索失败: {str(e)}"
