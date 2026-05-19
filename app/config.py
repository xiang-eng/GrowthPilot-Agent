import os
from pathlib import Path

from dotenv import load_dotenv
#以后要改模型名、数据路径，只改这个文件。

BASE_DIR = Path(__file__).resolve().parents[1]
#它用来找到项目根目录：

DATA_DIR = BASE_DIR / "data"

PRODUCT_PATH = DATA_DIR / "product.csv"
SALES_PATH = DATA_DIR / "sales.csv"
COMMENTS_PATH = DATA_DIR / "comments.csv"

load_dotenv(BASE_DIR / ".env")
#去项目根目录找 .env,这样比直接 load_dotenv() 更稳。
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

QWEN_MODEL = "qwen-plus"