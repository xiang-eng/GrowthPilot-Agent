from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

PLATFORM_RULES_PATH = KNOWLEDGE_BASE_DIR / "platform_rules.md"
CONTENT_STYLE_GUIDE_PATH = KNOWLEDGE_BASE_DIR / "content_style_guide.md"
COMPLIANCE_TERMS_PATH = KNOWLEDGE_BASE_DIR / "compliance_terms.md"


def read_text_file(file_path: Path) -> str:
    """
    读取文本文件内容。

    如果文件不存在，返回空字符串，避免程序直接崩溃。
    """
    if not file_path.exists():
        return ""

    return file_path.read_text(encoding="utf-8")


def load_platform_rules() -> str:
    """
    读取内容电商平台运营规则知识。
    """
    return read_text_file(PLATFORM_RULES_PATH)


def load_content_style_guide() -> str:
    """
    读取小红书 / 抖音内容风格知识。
    """
    return read_text_file(CONTENT_STYLE_GUIDE_PATH)


def load_compliance_terms() -> str:
    """
    读取合规风险词知识。
    """
    return read_text_file(COMPLIANCE_TERMS_PATH)


def merge_knowledge_sections(sections: list[str]) -> str:
    """
    合并多段知识库内容。

    空内容会自动过滤掉。
    """
    valid_sections = [
        section.strip()
        for section in sections
        if section and section.strip()
    ]

    return "\n\n".join(valid_sections)


def load_content_strategy_knowledge() -> str:
    """
    读取内容策略 Agent 需要的知识库内容。

    包括：
    1. 平台运营规则
    2. 内容风格指南
    """
    return merge_knowledge_sections(
        [
            load_platform_rules(),
            load_content_style_guide(),
        ]
    )


def load_compliance_knowledge() -> str:
    """
    读取合规审核 Agent 需要的知识库内容。

    包括：
    1. 平台运营规则
    2. 合规风险词
    """
    return merge_knowledge_sections(
        [
            load_platform_rules(),
            load_compliance_terms(),
        ]
    )


def load_all_knowledge() -> str:
    """
    读取全部轻量知识库内容。
    """
    return merge_knowledge_sections(
        [
            load_platform_rules(),
            load_content_style_guide(),
            load_compliance_terms(),
        ]
    )