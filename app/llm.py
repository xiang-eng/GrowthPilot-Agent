#专门负责调用通义千问大模型，以后所有 Agent 都不直接写 API 调用代码，而是统一调用：call_qwen()
import streamlit as st
from openai import OpenAI

from app.config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, QWEN_MODEL


def get_qwen_client() -> OpenAI:
    """
    创建通义千问客户端。
    """
    if not DASHSCOPE_API_KEY:
        st.error("没有找到 DASHSCOPE_API_KEY，请检查项目根目录下的 .env 文件。")
        st.stop()

    return OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )


client = get_qwen_client()


def call_qwen(prompt: str, temperature: float = 0.3) -> str:
    """
    调用通义千问模型。

    参数:
        prompt: 给大模型的任务说明
        temperature: 控制生成结果的随机性

    返回:
        大模型生成的文本结果
    """
    response = client.chat.completions.create(
        model=QWEN_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )

    return response.choices[0].message.content