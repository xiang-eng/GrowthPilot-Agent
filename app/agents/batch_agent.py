import pandas as pd

from app.llm import call_qwen
from app.prompt_loader import render_prompt


def build_batch_growth_prompt(
    selected_df: pd.DataFrame,
    selected_comments: pd.DataFrame,
) -> str:
    """
    构建多商品批量增长分析 Agent 的 Prompt。

    参数:
        selected_df: 用户选择的多个商品运营数据
        selected_comments: 用户选择商品对应的评论数据

    返回:
        给大模型的 Prompt 字符串
    """
    product_text = selected_df.to_string(index=False)
    comments_text = selected_comments.to_string(index=False)

    prompt = render_prompt(
        "batch_growth_prompt.txt",
        product_text=product_text,
        comments_text=comments_text,
    )

    return prompt


def run_batch_growth_agent(
    df: pd.DataFrame,
    comments: pd.DataFrame,
    selected_products: list[str],
) -> str:
    """
    运行多商品批量增长分析 Agent。

    参数:
        df: 商品运营数据表
        comments: 用户评论数据表
        selected_products: 用户选择的商品名称列表

    返回:
        多商品批量增长分析结果
    """
    if not selected_products:
        return "请至少选择一个商品后再运行多商品批量增长分析。"

    selected_df = df[df["product_name"].isin(selected_products)].copy()

    if selected_df.empty:
        return "没有找到选中的商品数据，请检查商品名称是否正确。"

    selected_product_ids = selected_df["product_id"].astype(str).tolist()

    selected_comments = comments[
        comments["product_id"].astype(str).isin(selected_product_ids)
    ].copy()

    prompt = build_batch_growth_prompt(
        selected_df=selected_df,
        selected_comments=selected_comments,
    )

    result = call_qwen(
        prompt=prompt,
        temperature=0.4,
    )

    return result