# 测试查看 Chroma 里的内容
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import os
import numpy

load_dotenv()
CHROMADB_PATH = os.getenv("CHROMADB_PATH")
embedding_model = OllamaEmbeddings(model="qwen3-embedding:4b")

# 加载已经存在的 Chroma 数据库
vector_store = Chroma(
    collection_name="user_1_docs",  # 替换为你实际的用户ID
    embedding_function=embedding_model,
    persist_directory=CHROMADB_PATH
)

# 获取并打印集合中的所有文档内容
collection = vector_store._collection
results = collection.get(include=["documents", "metadatas"])

print(f"知识库中共有 {len(results['documents'])} 个文本块：")
for i, doc in enumerate(results['documents']):
    print(f"--- 文本块 {i+1} ---")
    print(doc)
    print(f"元数据: {results['metadatas'][i]}\n")