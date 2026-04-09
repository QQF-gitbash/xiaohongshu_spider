"""全局配置"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COOKIE_FILE = BASE_DIR / "cookies.json"
DATA_DIR.mkdir(exist_ok=True)

# HTTP
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

# 小红书
XHS_BASE = "https://www.xiaohongshu.com"
XHS_API = "https://edith.xiaohongshu.com"

# AI
OPENAI_API_KEY = os.getenv("DASHSCOPE_API_KEY")       # 填你的 key
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_MODEL = "qwen-plus"
