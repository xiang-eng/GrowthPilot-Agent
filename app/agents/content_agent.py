import pandas as pd

from app.knowledge_service import load_content_strategy_knowledge
from app.llm import call_qwen
from app.prompt_loader import render_prompt
from app.rag_service import retrieve_knowledge


def build_content_strategy_prompt(
    product_info: pd.DataFrame,
    product_comments: pd.DataFrame,
) -> str:
    """
    构建内容策略 Agent 的 Prompt。

    参数:
        product_info: 当前选中商品的运营数据
        product_comments: 当前选中商品的用户评论

    返回:
        给大模型的 Prompt 字符串
    """
    product_text = product_info.to_string()
    comment_text = product_comments.to_string()

    prompt = render_prompt(
        "content_strategy_prompt.txt",
        product_text=product_text,
        comment_text=comment_text,
    )

    rag_query = (
        "请根据当前商品运营数据和用户评论，检索适合内容策略生成的"
        "内容平台规则、小红书内容风格、抖音脚本结构和合规表达建议。\n\n"
        f"商品运营数据：\n{product_text}\n\n"
        f"用户评论数据：\n{comment_text}"
    )

    try:
        knowledge_text = retrieve_knowledge(
            query=rag_query,
            top_k=3,
        )
    except Exception:
        knowledge_text = load_content_strategy_knowledge()

    if not knowledge_text:
        knowledge_text = load_content_strategy_knowledge()

    if knowledge_text:
        prompt = (
            f"{prompt}\n\n"
            "以下是从 ChromaDB 向量知识库检索到的内容平台规则和内容风格知识，"
            "请在生成内容策略时参考，但不要逐字照抄：\n"
            f"{knowledge_text}"
        )

    return prompt


def run_content_strategy_agent(
    df: pd.DataFrame,
    comments: pd.DataFrame,
    selected_product: str,
) -> str:
    """
    运行内容策略 Agent。

    参数:
        df: 商品运营数据表
        comments: 用户评论数据表
        selected_product: 用户在页面选择的商品名称

    返回:
        小红书和抖音内容运营方案
    """
    product_info = df[df["product_name"] == selected_product]

    product_id = product_info.iloc[0]["product_id"]

    product_comments = comments[
        comments["product_id"].astype(str) == str(product_id)
    ]

    prompt = build_content_strategy_prompt(
        product_info=product_info,
        product_comments=product_comments,
    )

    result = call_qwen(
        prompt=prompt,
        temperature=0.7,
    )

    return result