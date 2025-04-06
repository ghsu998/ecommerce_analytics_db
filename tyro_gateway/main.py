# tyro_gateway/main.py

import os
import json
import project_loader

from fastapi import FastAPI
from tyro_gateway.routers import router                # ✅ 主功能 API 集合點
from tyro_gateway.routers import github_webhook        # 🔁 GitHub webhook 自動部署
from tyro_gateway.utils import github_utils            # 🔍 查詢最新 commit 狀態
from tyro_gateway.routers import dev_tools             # 🛠️ 開發者工具
from tyro_gateway.routers import repo_docs             # 📘 自動化文件 API

from dotenv import load_dotenv
from tyro_gateway.env_loader import get_gpt_mode

load_dotenv()
GPT_MODE = get_gpt_mode()

app = FastAPI()

# ✅ 載入所有路由模組
app.include_router(router)
app.include_router(github_webhook.router)
app.include_router(github_utils.router)
app.include_router(dev_tools.router)
app.include_router(repo_docs.router)

# ✅ 同步目前 repo 狀態（供 GPT 使用）
PROJECT_STATE = project_loader.sync_project()
print(f"🧠 Project Loaded: {PROJECT_STATE['loaded']} files")
print("📄 Sample files:")
for path in PROJECT_STATE["sample"]:
    print("  -", path)

# ✅ 若 logs 資料夾存在，紀錄 Project Snapshot
try:
    os.makedirs("logs", exist_ok=True)
    with open("logs/project_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(PROJECT_STATE, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"⚠️ Failed to write snapshot log: {e}")

# ✅ 開發用途：查詢載入狀態
@app.get("/api/dev/project_status")
def get_project_state():
    return PROJECT_STATE

# ✅ 健康檢查
@app.get("/")
def read_root():
    return {"message": f"Hello from TYRO Gateway — Mode: {GPT_MODE}"}
