import hashlib
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from app.config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
)


KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

COLLECTION_NAME = "growthpilot_knowledge"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 80


def read_markdown_file(file_path: Path) -> str:
    """
    读取 Markdown 文件内容。

    如果文件不存在，返回空字符串，避免程序直接崩溃。
    """
    if not file_path.exists():
        return ""

    return file_path.read_text(encoding="utf-8")


def load_knowledge_documents() -> List[Dict[str, str]]:
    """
    读取 knowledge_base 目录下的 Markdown 知识库文件。
    """
    knowledge_files = [
        KNOWLEDGE_BASE_DIR / "platform_rules.md",
        KNOWLEDGE_BASE_DIR / "content_style_guide.md",
        KNOWLEDGE_BASE_DIR / "compliance_terms.md",
    ]

    documents: List[Dict[str, str]] = []

    for file_path in knowledge_files:
        content = read_markdown_file(file_path)

        if content.strip():
            documents.append(
                {
                    "source": file_path.name,
                    "content": content,
                }
            )

    return documents


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    将长文本切分为多个小片段。
    """
    clean_text = text.strip()

    if not clean_text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap 不能小于 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size")

    chunks: List[str] = []
    start = 0

    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def normalize_embedding(vector: List[float]) -> List[float]:
    """
    对 embedding 向量做 L2 归一化。
    """
    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def resize_embedding(
    vector: List[float],
    dimension: int = EMBEDDING_DIMENSION,
) -> List[float]:
    """
    将任意维度 embedding 压缩或扩展到固定维度。

    这样可以保证 ChromaDB collection 的维度稳定。
    默认 hash embedding 和 DashScope embedding 都会落到同一维度。
    """
    if dimension <= 0:
        raise ValueError("dimension 必须大于 0")

    if not vector:
        return [0.0 for _ in range(dimension)]

    resized = [0.0 for _ in range(dimension)]

    for index, value in enumerate(vector):
        bucket = index % dimension
        resized[bucket] += float(value)

    return normalize_embedding(resized)


def build_hash_embedding(
    text: str,
    dimension: int = EMBEDDING_DIMENSION,
) -> List[float]:
    """
    使用本地哈希方法生成确定性 embedding。

    这是一个轻量本地 embedding，用于保证项目无需额外 API Key 也能运行。
    """
    if dimension <= 0:
        raise ValueError("dimension 必须大于 0")

    vector = [0.0 for _ in range(dimension)]
    normalized_text = text.lower().strip()

    if not normalized_text:
        return vector

    tokens = []

    for index, char in enumerate(normalized_text):
        if char.strip():
            tokens.append(char)

        if index < len(normalized_text) - 1:
            bigram = normalized_text[index : index + 2].strip()
            if bigram:
                tokens.append(bigram)

    for token in tokens:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % dimension
        sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
        vector[bucket] += sign

    return normalize_embedding(vector)


def get_dashscope_embedding_client() -> OpenAI:
    """
    获取 DashScope OpenAI 兼容模式客户端。
    """
    if not DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 未配置，无法使用 DashScope Embedding")

    return OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )


def build_dashscope_embedding(text: str) -> List[float]:
    """
    使用 DashScope Embedding 生成向量。

    返回前会压缩到 EMBEDDING_DIMENSION，保证和本地 hash embedding 维度一致。
    """
    if not text.strip():
        return [0.0 for _ in range(EMBEDDING_DIMENSION)]

    client = get_dashscope_embedding_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    embedding = response.data[0].embedding

    return resize_embedding(
        vector=embedding,
        dimension=EMBEDDING_DIMENSION,
    )


def build_embedding(text: str) -> List[float]:
    """
    根据配置生成 embedding。

    EMBEDDING_PROVIDER=hash：
        使用本地哈希 embedding。

    EMBEDDING_PROVIDER=dashscope：
        优先使用 DashScope Embedding。
        如果 DashScope 调用失败，自动 fallback 到本地哈希 embedding。
    """
    if EMBEDDING_PROVIDER == "dashscope":
        try:
            return build_dashscope_embedding(text)
        except Exception:
            return build_hash_embedding(text)

    return build_hash_embedding(text)


def get_embedding_runtime_info() -> Dict[str, Any]:
    """
    返回当前 embedding 配置信息。
    """
    return {
        "embedding_provider": EMBEDDING_PROVIDER,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "fallback_provider": "hash",
    }


def get_chroma_client():
    """
    获取 ChromaDB 本地持久化客户端。
    """
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(VECTOR_DB_DIR))


def reset_knowledge_collection() -> None:
    """
    删除旧的知识库 collection。

    用于重新构建向量库。
    """
    client = get_chroma_client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass


def get_knowledge_collection():
    """
    获取或创建知识库 collection。
    """
    client = get_chroma_client()

    return client.get_or_create_collection(name=COLLECTION_NAME)


def build_knowledge_chunks() -> List[Dict[str, str]]:
    """
    从 Markdown 知识库构建切分后的知识片段。
    """
    documents = load_knowledge_documents()
    chunks: List[Dict[str, str]] = []

    for document in documents:
        source = document["source"]
        content = document["content"]
        text_chunks = split_text_into_chunks(content)

        for index, chunk in enumerate(text_chunks):
            chunks.append(
                {
                    "id": f"{source}_{index}",
                    "source": source,
                    "content": chunk,
                }
            )

    return chunks


def index_knowledge_base(reset: bool = True) -> int:
    """
    将 knowledge_base 中的知识片段写入 ChromaDB。

    参数:
        reset: 是否先删除旧 collection，再重新写入。

    返回:
        写入的知识片段数量。
    """
    if reset:
        reset_knowledge_collection()

    collection = get_knowledge_collection()
    chunks = build_knowledge_chunks()

    if not chunks:
        return 0

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [{"source": chunk["source"]} for chunk in chunks]
    embeddings = [build_embedding(chunk["content"]) for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return len(chunks)


def ensure_knowledge_index() -> None:
    """
    确保 ChromaDB 中已经存在知识库索引。

    如果 collection 为空，则自动构建索引。
    """
    collection = get_knowledge_collection()

    if collection.count() == 0:
        index_knowledge_base(reset=True)


def retrieve_knowledge_with_details(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    根据 query 从 ChromaDB 检索相关知识片段，并返回可用于 Trace 的详细信息。
    """
    runtime_info = get_embedding_runtime_info()

    if not query.strip():
        return {
            "retrieved_text": "",
            "query": query,
            "top_k": top_k,
            "sources": [],
            "chunk_count": 0,
            "used_chromadb": False,
            **runtime_info,
        }

    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")

    ensure_knowledge_index()

    collection = get_knowledge_collection()
    query_embedding = build_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    retrieved_sections: List[str] = []
    sources: List[str] = []

    for index, document in enumerate(documents):
        source = ""

        if index < len(metadatas) and metadatas[index]:
            source = metadatas[index].get("source", "")

        if source:
            sources.append(source)
            retrieved_sections.append(f"来源：{source}\n{document}")
        else:
            retrieved_sections.append(document)

    unique_sources = list(dict.fromkeys(sources))
    retrieved_text = "\n\n---\n\n".join(retrieved_sections)

    return {
        "retrieved_text": retrieved_text,
        "query": query,
        "top_k": top_k,
        "sources": unique_sources,
        "chunk_count": len(documents),
        "used_chromadb": True,
        **runtime_info,
    }


def retrieve_knowledge(query: str, top_k: int = 3) -> str:
    """
    根据 query 从 ChromaDB 检索相关知识片段。

    返回拼接后的文本，方便注入 Prompt。
    """
    result = retrieve_knowledge_with_details(
        query=query,
        top_k=top_k,
    )

    return result["retrieved_text"]


if __name__ == "__main__":
    runtime_info = get_embedding_runtime_info()

    print("Embedding 配置信息：")
    print(f"provider: {runtime_info['embedding_provider']}")
    print(f"model: {runtime_info['embedding_model']}")
    print(f"dimension: {runtime_info['embedding_dimension']}")
    print(f"fallback_provider: {runtime_info['fallback_provider']}")

    total_chunks = index_knowledge_base(reset=True)
    print(f"\n知识库索引构建完成，写入片段数: {total_chunks}")

    demo_query = "小红书内容生成需要注意哪些合规表达？"
    retrieved_result = retrieve_knowledge_with_details(demo_query, top_k=3)

    print("\n检索示例：")
    print(retrieved_result["retrieved_text"])

    print("\n检索元信息：")
    print(f"query: {retrieved_result['query']}")
    print(f"top_k: {retrieved_result['top_k']}")
    print(f"sources: {retrieved_result['sources']}")
    print(f"chunk_count: {retrieved_result['chunk_count']}")
    print(f"used_chromadb: {retrieved_result['used_chromadb']}")
    print(f"embedding_provider: {retrieved_result['embedding_provider']}")
    print(f"embedding_model: {retrieved_result['embedding_model']}")
    print(f"embedding_dimension: {retrieved_result['embedding_dimension']}")