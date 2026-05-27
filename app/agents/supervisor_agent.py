import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

from app.agents.compliance_agent import run_compliance_agent
from app.agents.content_agent import run_content_strategy_agent
from app.agents.insight_agent import run_user_insight_agent
from app.agents.sales_agent import run_sales_analysis_agent
from app.rag_service import get_embedding_runtime_info, retrieve_knowledge_with_details


def generate_run_id() -> str:
    """
    生成一次 Supervisor 工作流运行的唯一 ID。
    """
    return f"run_{uuid.uuid4().hex[:12]}"


def notify_progress(
    progress_callback: Optional[Callable[[int, str], None]],
    progress: int,
    message: str,
) -> None:
    """
    通知前端当前工作流执行进度。
    """
    if progress_callback is not None:
        progress_callback(progress, message)


def build_default_rag_context(
    agent_name: str,
    query: str = "",
    error: str = "",
) -> Dict[str, Any]:
    """
    构建默认 RAG Trace 上下文。
    """
    embedding_info = get_embedding_runtime_info()

    return {
        "enabled": True,
        "agent": agent_name,
        "query": query[:500],
        "top_k": 3,
        "sources": [],
        "chunk_count": 0,
        "used_chromadb": False,
        "fallback_used": True,
        "retrieved_text_preview": "",
        "error": error,
        "embedding_provider": embedding_info["embedding_provider"],
        "embedding_model": embedding_info["embedding_model"],
        "embedding_dimension": embedding_info["embedding_dimension"],
        "fallback_provider": embedding_info["fallback_provider"],
    }


def build_content_rag_trace_context(
    df: pd.DataFrame,
    comments: pd.DataFrame,
    selected_product: str,
) -> Dict[str, Any]:
    """
    构建内容策略 Agent 的 RAG Trace 元信息。
    """
    product_info = df[df["product_name"] == selected_product]

    if product_info.empty:
        return {
            "rag_context": build_default_rag_context(
                agent_name="Content Strategy Agent",
                error=f"未找到选中商品：{selected_product}",
            )
        }

    product_id = product_info.iloc[0]["product_id"]

    product_comments = comments[
        comments["product_id"].astype(str) == str(product_id)
    ]

    product_text = product_info.to_string()
    comment_text = product_comments.to_string()

    rag_query = (
        "请根据当前商品运营数据和用户评论，检索适合内容策略生成的"
        "内容平台规则、小红书内容风格、抖音脚本结构和合规表达建议。\n\n"
        f"商品运营数据：\n{product_text}\n\n"
        f"用户评论数据：\n{comment_text}"
    )

    try:
        rag_result = retrieve_knowledge_with_details(
            query=rag_query,
            top_k=3,
        )

        return {
            "rag_context": {
                "enabled": True,
                "agent": "Content Strategy Agent",
                "query": rag_result["query"][:500],
                "top_k": rag_result["top_k"],
                "sources": rag_result["sources"],
                "chunk_count": rag_result["chunk_count"],
                "used_chromadb": rag_result["used_chromadb"],
                "fallback_used": False,
                "retrieved_text_preview": rag_result["retrieved_text"][:300],
                "error": "",
                "embedding_provider": rag_result.get("embedding_provider", ""),
                "embedding_model": rag_result.get("embedding_model", ""),
                "embedding_dimension": rag_result.get("embedding_dimension", 0),
                "fallback_provider": rag_result.get("fallback_provider", "hash"),
            }
        }

    except Exception as error:
        return {
            "rag_context": build_default_rag_context(
                agent_name="Content Strategy Agent",
                query=rag_query,
                error=str(error),
            )
        }


def build_compliance_rag_trace_context(content: str) -> Dict[str, Any]:
    """
    构建合规审核 Agent 的 RAG Trace 元信息。
    """
    rag_query = (
        "请根据以下待审核营销内容，检索最相关的平台规则、合规风险词、"
        "绝对化表达、功效承诺、医疗化表达、虚假稀缺和用户评价夸大风险：\n\n"
        f"{content}"
    )

    try:
        rag_result = retrieve_knowledge_with_details(
            query=rag_query,
            top_k=3,
        )

        return {
            "rag_context": {
                "enabled": True,
                "agent": "Compliance Agent",
                "query": rag_result["query"][:500],
                "top_k": rag_result["top_k"],
                "sources": rag_result["sources"],
                "chunk_count": rag_result["chunk_count"],
                "used_chromadb": rag_result["used_chromadb"],
                "fallback_used": False,
                "retrieved_text_preview": rag_result["retrieved_text"][:300],
                "error": "",
                "embedding_provider": rag_result.get("embedding_provider", ""),
                "embedding_model": rag_result.get("embedding_model", ""),
                "embedding_dimension": rag_result.get("embedding_dimension", 0),
                "fallback_provider": rag_result.get("fallback_provider", "hash"),
            }
        }

    except Exception as error:
        return {
            "rag_context": build_default_rag_context(
                agent_name="Compliance Agent",
                query=rag_query,
                error=str(error),
            )
        }


def run_agent_with_trace(
    run_id: str,
    step_name: str,
    step_description: str,
    input_summary: str,
    agent_func: Callable[..., str],
    *args: Any,
    extra_trace_fields: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Tuple[str, Dict[str, Any]]:
    """
    运行单个 Agent，并记录执行日志。
    """
    start_time = time.perf_counter()

    try:
        result = agent_func(*args, **kwargs)
        duration = time.perf_counter() - start_time

        trace = {
            "run_id": run_id,
            "step": step_name,
            "description": step_description,
            "input_summary": input_summary,
            "status": "success",
            "duration_seconds": round(duration, 2),
            "output_preview": result[:200],
            "error": "",
        }

        if extra_trace_fields:
            trace.update(extra_trace_fields)

        return result, trace

    except Exception as error:
        duration = time.perf_counter() - start_time

        trace = {
            "run_id": run_id,
            "step": step_name,
            "description": step_description,
            "input_summary": input_summary,
            "status": "failed",
            "duration_seconds": round(duration, 2),
            "output_preview": "",
            "error": str(error),
        }

        if extra_trace_fields:
            trace.update(extra_trace_fields)

        return "", trace


def run_supervisor_workflow(
    df: pd.DataFrame,
    comments: pd.DataFrame,
    selected_product: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Dict[str, Any]:
    """
    运行 Supervisor 多 Agent 工作流。
    """
    run_id = generate_run_id()
    traces: List[Dict[str, Any]] = []

    notify_progress(
        progress_callback,
        5,
        f"已创建工作流运行 ID：{run_id}",
    )

    notify_progress(
        progress_callback,
        15,
        "正在运行销售数据分析 Agent...",
    )

    sales_analysis, sales_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="销售数据分析 Agent",
        step_description="分析商品 GMV、CTR、CVR、退款率等经营指标",
        input_summary=(
            f"商品运营数据行数：{len(df)}；"
            f"字段：{', '.join(df.columns.tolist())}"
        ),
        agent_func=run_sales_analysis_agent,
        df=df,
    )
    traces.append(sales_trace)

    notify_progress(
        progress_callback,
        35,
        "销售数据分析 Agent 已完成，正在运行用户评论洞察 Agent...",
    )

    user_insight, insight_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="用户评论洞察 Agent",
        step_description="从用户评论中提取痛点、正反馈、负反馈和内容机会",
        input_summary=(
            f"用户评论数据行数：{len(comments)}；"
            f"字段：{', '.join(comments.columns.tolist())}"
        ),
        agent_func=run_user_insight_agent,
        comments=comments,
    )
    traces.append(insight_trace)

    notify_progress(
        progress_callback,
        55,
        "用户评论洞察 Agent 已完成，正在运行内容策略 Agent...",
    )

    content_rag_trace_context = build_content_rag_trace_context(
        df=df,
        comments=comments,
        selected_product=selected_product,
    )

    content_strategy, content_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="内容策略 Agent",
        step_description="基于商品数据、用户评论和 RAG 检索结果生成小红书笔记、抖音脚本和发布建议",
        input_summary=(
            f"选中商品：{selected_product}；"
            f"商品运营数据行数：{len(df)}；"
            f"用户评论数据行数：{len(comments)}"
        ),
        agent_func=run_content_strategy_agent,
        extra_trace_fields=content_rag_trace_context,
        df=df,
        comments=comments,
        selected_product=selected_product,
    )
    traces.append(content_trace)

    notify_progress(
        progress_callback,
        75,
        "内容策略 Agent 已完成，正在运行合规审核 Agent...",
    )

    compliance_rag_trace_context = build_compliance_rag_trace_context(
        content=content_strategy,
    )

    compliance_review, compliance_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="合规审核 Agent",
        step_description="基于生成内容和 RAG 检索结果审核是否存在夸大宣传、绝对化表达等风险",
        input_summary=(
            f"待审核内容长度：{len(content_strategy)} 字符；"
            f"来源：内容策略 Agent 输出"
        ),
        agent_func=run_compliance_agent,
        extra_trace_fields=compliance_rag_trace_context,
        content=content_strategy,
    )
    traces.append(compliance_trace)

    notify_progress(
        progress_callback,
        100,
        "Supervisor 多 Agent 工作流执行完成。",
    )

    return {
        "run_id": run_id,
        "sales_analysis": sales_analysis,
        "user_insight": user_insight,
        "content_strategy": content_strategy,
        "compliance_review": compliance_review,
        "traces": traces,
    }