from app.config import BASE_DIR
#BASE_DIR 是项目根目录。

PROMPT_DIR = BASE_DIR / "app" / "prompts"
#Prompt 文件统一放在 app/prompts 里面

def load_prompt_template(file_name: str) -> str:
    #这个函数专门负责读 Prompt 文件。
    """
    根据文件名读取 Prompt 模板。

    参数:
        file_name: Prompt 文件名，例如 sales_analysis_prompt.txt

    返回:
        Prompt 模板字符串
    """
    prompt_path = PROMPT_DIR / file_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt 模板文件不存在: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def render_prompt(file_name: str, **kwargs) -> str:
    #读取 Prompt 模板
    #然后把变量填进去
    """
    读取 Prompt 模板，并把变量填充进去。

    参数:
        file_name: Prompt 文件名
        **kwargs: 要填充到 Prompt 里的变量

    返回:
        填充变量后的完整 Prompt
    """
    template = load_prompt_template(file_name)

    return template.format(**kwargs)