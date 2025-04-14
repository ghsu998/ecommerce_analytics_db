# tyro_gateway/env_loader.py

import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

def get_gpt_mode():
    """
    回傳目前 GPT 啟動模式，可為：
    - development（開發者模式）
    - root_user（Root User）
    - team_user（Team User）
    - chat（普通 GPT 模式）
    """
    return os.getenv("GPT_MODE", "chat")

