import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
PRODUCT_PATH = DATA_DIR / "product.csv"
SALES_PATH = DATA_DIR / "sales.csv"
COMMENTS_PATH = DATA_DIR / "comments.csv"

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


def get_float_env(
    key: str,
    default: float,
) -> float:
    """
    从环境变量中读取 float 类型配置。

    如果环境变量不存在或无法转换为 float，则返回默认值。
    """
    value = os.getenv(key)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


def get_int_env(
    key: str,
    default: int,
) -> int:
    """
    从环境变量中读取 int 类型配置。

    如果环境变量不存在或无法转换为 int，则返回默认值。
    """
    value = os.getenv(key)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "").strip()

DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
).strip()

QWEN_MODEL = os.getenv(
    "QWEN_MODEL",
    "qwen-plus",
).strip()

QWEN_TEMPERATURE = get_float_env(
    "QWEN_TEMPERATURE",
    0.7,
)

EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER",
    "hash",
).strip().lower()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-v4",
).strip()

EMBEDDING_DIMENSION = get_int_env(
    "EMBEDDING_DIMENSION",
    64,
)