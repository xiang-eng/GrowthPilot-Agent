from app.llm import call_qwen
from app.prompt_loader import render_prompt


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