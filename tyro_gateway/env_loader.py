# tyro_gateway/env_loader.py

import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

def get_gpt_mode():
    """
    回傳目前 GPT 啟動模式，可為：
    - dev（開發者模式）
    - ops_root（營運 Root）
    - ops_team（團隊協作）
    - chat（普通 GPT 模式）
    """
    return os.getenv("GPT_MODE", "chat")
