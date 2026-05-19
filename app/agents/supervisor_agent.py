#它负责一键串联所有 Agent：
import time
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd

from app.agents.compliance_agent import run_compliance_agent
from app.agents.content_agent import run_content_strategy_agent
from app.agents.insight_agent import run_user_insight_agent
from app.agents.sales_agent import run_sales_analysis_agent


def run_agent_with_trace(
    step_name: str,
    step_description: str,
    agent_func: Callable[..., str],
    *args: Any,
    **kwargs: Any,
) -> Tuple[str, Dict[str, Any]]:
    """
    运行单个 Agent，并记录执行日志。

    参数:
        step_name: 当前步骤名称
        step_description: 当前步骤说明
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
            "step": step_name,
            "description": step_description,
            "status": "success",
            "duration_seconds": round(duration, 2),
            "output_preview": result[:200],
            "error": "",
        }

        return result, trace

    except Exception as error:
        duration = time.perf_counter() - start_time

        trace = {
            "step": step_name,
            "description": step_description,
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

    返回:
        包含多个 Agent 输出结果和执行日志的字典
    """
    traces: List[Dict[str, Any]] = []

    sales_analysis, sales_trace = run_agent_with_trace(
        step_name="销售数据分析 Agent",
        step_description="分析商品 GMV、CTR、CVR、退款率等经营指标",
        agent_func=run_sales_analysis_agent,
        df=df,
    )
    traces.append(sales_trace)

    user_insight, insight_trace = run_agent_with_trace(
        step_name="用户评论洞察 Agent",
        step_description="从用户评论中提取痛点、正反馈、负反馈和内容机会",
        agent_func=run_user_insight_agent,
        comments=comments,
    )
    traces.append(insight_trace)

    content_strategy, content_trace = run_agent_with_trace(
        step_name="内容策略 Agent",
        step_description="基于商品数据和评论生成小红书笔记、抖音脚本和发布建议",
        agent_func=run_content_strategy_agent,
        df=df,
        comments=comments,
        selected_product=selected_product,
    )
    traces.append(content_trace)

    compliance_review, compliance_trace = run_agent_with_trace(
        step_name="合规审核 Agent",
        step_description="审核生成内容是否存在夸大宣传、绝对化表达等风险",
        agent_func=run_compliance_agent,
        content=content_strategy,
    )
    traces.append(compliance_trace)

    return {
        "sales_analysis": sales_analysis,
        "user_insight": user_insight,
        "content_strategy": content_strategy,
        "compliance_review": compliance_review,
        "traces": traces,
    }