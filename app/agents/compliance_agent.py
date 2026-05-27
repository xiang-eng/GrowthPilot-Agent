from app.knowledge_service import load_compliance_knowledge
from app.llm import call_qwen
from app.prompt_loader import render_prompt
from app.rag_service import retrieve_knowledge_with_details


def build_compliance_prompt(content: str) -> str:
    """
    构建合规审核 Agent 的 Prompt。

    参数:
        content: 需要审核的小红书文案、抖音脚本或营销内容

    返回:
        给大模型的 Prompt 字符串
    """
    prompt = render_prompt(
        "compliance_prompt.txt",
        content=content,
    )

    rag_query = (
        "请根据以下待审核营销内容，检索最相关的平台规则、合规风险词、"
        "绝对化表达、功效承诺、医疗化表达、虚假稀缺和用户评价夸大风险：\n\n"
        f"{content}"
    )

    rag_metadata = {
        "query": rag_query,
        "top_k": 3,
        "sources": [],
        "chunk_count": 0,
        "used_chromadb": False,
        "fallback_used": False,
    }

    try:
        rag_result = retrieve_knowledge_with_details(
            query=rag_query,
            top_k=3,
        )
        knowledge_text = rag_result["retrieved_text"]
        rag_metadata.update(
            {
                "query": rag_result["query"],
                "top_k": rag_result["top_k"],
                "sources": rag_result["sources"],
                "chunk_count": rag_result["chunk_count"],
                "used_chromadb": rag_result["used_chromadb"],
            }
        )
    except Exception:
        knowledge_text = load_compliance_knowledge()
        rag_metadata["fallback_used"] = True

    if not knowledge_text:
        knowledge_text = load_compliance_knowledge()
        rag_metadata["fallback_used"] = True

    if knowledge_text:
        prompt = (
            f"{prompt}\n\n"
            "以下是从 ChromaDB 向量知识库检索到的平台规则和合规风险知识，"
            "请在审核内容时参考，重点识别绝对化表达、功效承诺、医疗化表达、"
            "虚假稀缺和用户评价夸大风险：\n"
            f"{knowledge_text}\n\n"
            "RAG 检索元信息：\n"
            f"- query: {rag_metadata['query'][:300]}\n"
            f"- top_k: {rag_metadata['top_k']}\n"
            f"- sources: {rag_metadata['sources']}\n"
            f"- chunk_count: {rag_metadata['chunk_count']}\n"
            f"- used_chromadb: {rag_metadata['used_chromadb']}\n"
            f"- fallback_used: {rag_metadata['fallback_used']}"
        )

    return prompt


def run_compliance_agent(content: str) -> str:
    """
    运行合规审核 Agent。

    参数:
        content: 需要审核的内容

    返回:
        合规审核结果
    """
    prompt = build_compliance_prompt(content)

    result = call_qwen(
        prompt=prompt,
        temperature=0.2,
    )

    return result