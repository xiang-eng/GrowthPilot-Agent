import pandas as pd

from app.llm import call_qwen
from app.prompt_loader import render_prompt


def build_user_insight_prompt(comments: pd.DataFrame) -> str:
    """
    构建用户评论洞察 Agent 的 Prompt。

    参数:
        comments: 用户评论数据表

    返回:
        给大模型的 Prompt 字符串
    """
    comments_text = comments.to_string()

    prompt = render_prompt(
        "user_insight_prompt.txt",
        comments_text=comments_text,
    )

    return prompt


def run_user_insight_agent(comments: pd.DataFrame) -> str:
    """
    运行用户评论洞察 Agent。

    参数:
        comments: 用户评论数据表

    返回:
        用户评论洞察分析结果
    """
    prompt = build_user_insight_prompt(comments)

    result = call_qwen(
        prompt=prompt,
        temperature=0.3,
    )

    return result