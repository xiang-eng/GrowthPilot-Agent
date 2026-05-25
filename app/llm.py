#专门负责调用通义千问大模型，以后所有 Agent 都不直接写 API 调用代码，而是统一调用：call_qwen()
from typing import Optional

from openai import OpenAI

from app.config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    QWEN_MODEL,
    QWEN_TEMPERATURE,
)


def validate_llm_config() -> None:
    """
    检查大模型调用所需配置是否完整。

    如果没有配置 DASHSCOPE_API_KEY，则抛出清晰错误。
    """
    if not DASHSCOPE_API_KEY:
        raise RuntimeError(
            "未检测到 DASHSCOPE_API_KEY。"
            "请在项目根目录创建 .env 文件，并填写："
            "DASHSCOPE_API_KEY=你的DashScope_API_Key"
        )


def get_qwen_client() -> OpenAI:
    """
    创建 DashScope OpenAI 兼容模式客户端。

    返回:
        OpenAI 客户端实例
    """
    validate_llm_config()

    return OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
    )


def call_qwen(
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    调用通义千问模型。

    参数:
        prompt: 输入给大模型的 Prompt
        model: 可选模型名称。如果不传，则使用 .env 中的 QWEN_MODEL
        temperature: 可选生成随机性。如果不传，则使用 .env 中的 QWEN_TEMPERATURE

    返回:
        大模型生成的文本结果
    """
    client = get_qwen_client()

    selected_model = model or QWEN_MODEL

    selected_temperature = (
        QWEN_TEMPERATURE
        if temperature is None
        else temperature
    )

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "role": "system",
                "content": "你是一个擅长内容电商运营分析和内容策略生成的 AI 助手。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=selected_temperature,
    )

    content = response.choices[0].message.content

    if content is None:
        return ""

    return content