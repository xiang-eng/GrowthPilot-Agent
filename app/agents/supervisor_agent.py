import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

from app.agents.compliance_agent import run_compliance_agent
from app.agents.content_agent import run_content_strategy_agent
from app.agents.insight_agent import run_user_insight_agent
from app.agents.sales_agent import run_sales_analysis_agent


def generate_run_id() -> str:
    """
    生成一次 Supervisor 工作流运行的唯一 ID。

    返回:
        形如 run_xxxxxxxxxxxx 的字符串
    """
    return f"run_{uuid.uuid4().hex[:12]}"


def notify_progress(
    progress_callback: Optional[Callable[[int, str], None]],
    progress: int,
    message: str,
) -> None:
    """
    通知前端当前工作流执行进度。

    参数:
        progress_callback: 前端传入的进度更新函数
        progress: 当前进度，范围 0-100
        message: 当前执行状态说明
    """
    if progress_callback is not None:
        progress_callback(progress, message)


def run_agent_with_trace(
    run_id: str,
    step_name: str,
    step_description: str,
    input_summary: str,
    agent_func: Callable[..., str],
    *args: Any,
    **kwargs: Any,
) -> Tuple[str, Dict[str, Any]]:
    """
    运行单个 Agent，并记录执行日志。

    参数:
        run_id: 当前 Supervisor 工作流运行 ID
        step_name: 当前步骤名称
        step_description: 当前步骤说明
        input_summary: 当前 Agent 的输入摘要
        agent_func: 要执行的 Agent 函数
        *args: 传给 Agent 函数的位置参数
        **kwargs: 传给 Agent 函数的关键字参数

    返回:
        result: Agent 的输出结果
        trace: 当前 Agent 的执行日志
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

        return "", trace


def run_supervisor_workflow(
    df: pd.DataFrame,
    comments: pd.DataFrame,
    selected_product: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Dict[str, Any]:
    """
    运行 Supervisor 多 Agent 工作流。

    Supervisor Agent 负责按顺序调度多个专业 Agent：

    1. 销售数据分析 Agent
    2. 用户评论洞察 Agent
    3. 内容策略 Agent
    4. 合规审核 Agent

    参数:
        df: 商品运营数据表
        comments: 用户评论数据表
        selected_product: 用户选择的商品名称
        progress_callback: 可选进度回调函数，用于前端展示执行进度

    返回:
        包含多个 Agent 输出结果、run_id 和执行日志的字典
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

    content_strategy, content_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="内容策略 Agent",
        step_description="基于商品数据和评论生成小红书笔记、抖音脚本和发布建议",
        input_summary=(
            f"选中商品：{selected_product}；"
            f"商品运营数据行数：{len(df)}；"
            f"用户评论数据行数：{len(comments)}"
        ),
        agent_func=run_content_strategy_agent,
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

    compliance_review, compliance_trace = run_agent_with_trace(
        run_id=run_id,
        step_name="合规审核 Agent",
        step_description="审核生成内容是否存在夸大宣传、绝对化表达等风险",
        input_summary=(
            f"待审核内容长度：{len(content_strategy)} 字符；"
            f"来源：内容策略 Agent 输出"
        ),
        agent_func=run_compliance_agent,
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