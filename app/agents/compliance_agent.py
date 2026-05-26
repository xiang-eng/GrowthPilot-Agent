from app.knowledge_service import load_compliance_knowledge
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
    knowledge_text = load_compliance_knowledge()

    prompt = render_prompt(
        "compliance_prompt.txt",
        content=content,
    )

    if knowledge_text:
        prompt = (
            f"{prompt}\n\n"
            "以下是平台规则和合规风险词知识库，请在审核内容时参考，"
            "重点识别绝对化表达、功效承诺、医疗化表达、虚假稀缺和用户评价夸大风险：\n"
            f"{knowledge_text}"
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