from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embedding_model = OllamaEmbeddings(model="qwen3-embedding:4b")
from dotenv import load_dotenv
import os
# 读取项目根目录下的 .env 文件
load_dotenv()
CHROMADB_PATH = os.getenv("CHROMADB_PATH")

def process_and_store_file(file_path:str,user_id:int):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path,encoding="utf-8")
    else:
        print("Invalid file type")
        return
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        add_start_index=True
    )

    all_splits = text_splitter.split_documents(docs)

    vector_store = Chroma(
        collection_name=f"user_{user_id}_docs",
        embedding_function=embedding_model,
        persist_directory=CHROMADB_PATH
    )

    vector_store.add_documents(all_splits)
    print(f"Finished processing  用户 {user_id} 的知识库更新完毕！存入 {len(all_splits)} 个文本块")

# 向量化查询
def retrieve_user_knowledge(
        query: str,
        user_id: int,
        top_k: int = 5,
        min_score: float = 0.65
) -> str | None:
    """
    供智能体调用的检索工具：只查当前用户的专属知识库。
    只有相关度达到 min_score 的内容，才返回给大模型。
    """
    # 连接到该用户的专属库
    vector_store = Chroma(
        collection_name=f"user_{user_id}_docs",
        embedding_function=embedding_model,
        persist_directory=CHROMADB_PATH
    )

    result = vector_store.similarity_search_with_relevance_scores(query, k=top_k)

    # docs = [for doc,score in result if score >= min_score]
    docs = []
    for doc,score in result:
        if score >= min_score:
            docs.append(doc)


    if len(docs) <= 0:
        return None

    return "\n".join(doc.page_content for doc in docs)