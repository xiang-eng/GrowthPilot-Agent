#专门负责销售数据分析 Agent
import pandas as pd

from app.llm import call_qwen
from app.prompt_loader import render_prompt


def build_sales_analysis_prompt(df: pd.DataFrame) -> str:
    """
    构建销售数据分析 Agent 的 Prompt。

    参数:
        df: 已经合并并计算好指标的商品运营数据

    返回:
        给大模型的 Prompt 字符串
    """
    data_text = df.to_string()

    prompt = render_prompt(
        "sales_analysis_prompt.txt",
        data_text=data_text,
    )

    return prompt


def run_sales_analysis_agent(df: pd.DataFrame) -> str:
    """
    运行销售数据分析 Agent。

    参数:
        df: 已经合并并计算好指标的商品运营数据

    返回:
        销售数据分析结果
    """
    prompt = build_sales_analysis_prompt(df)

    result = call_qwen(
        prompt=prompt,
        temperature=0.3,
    )

    return result