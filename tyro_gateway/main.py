# tyro_gateway/main.py

import os
import json
import project_loader

from fastapi import FastAPI
from dotenv import load_dotenv
from tyro_gateway.env_loader import get_gpt_mode

# ✅ Step 1: 載入 .env 並取得 GPT 模式設定（dev / ops_root / ops_team / chat）
load_dotenv()
GPT_MODE = get_gpt_mode()

# ✅ Step 2: 初始化 FastAPI 應用
app = FastAPI()
print(f"🧠 GPT Gateway 啟動模式：{GPT_MODE}")

# ✅ Step 3: 共用模組（任何身份都會載入）
from tyro_gateway.routers import dev_tools, github_webhook
from tyro_gateway.utils import github_utils

app.include_router(dev_tools.router)         # 🛠️ 開發者工具（project tree 等）
app.include_router(github_webhook.router)    # 🔁 GitHub Webhook for 自動部署
app.include_router(github_utils.router)      # 🔍 Git commit 狀態查詢 API

# ✅ Step 4: 根據模式載入對應模組
if GPT_MODE == "dev":
    # 開發模式：載入所有開發者需要的模組
    from tyro_gateway.routers import router, repo_docs
    app.include_router(router)              # ✅ 整合主功能 API（career、tax、strategy 等）
    app.include_router(repo_docs.router)    # 📘 Git repo 掃描 / 解析 / 依賴分析

elif GPT_MODE == "ops_root":
    # 運營 Root：具備全權操作數據模組
    from tyro_gateway.routers import (
        strategy, career, tax, investment, writing
    )
    app.include_router(strategy.router)
    app.include_router(career.router)
    app.include_router(tax.router)
    app.include_router(investment.router)
    app.include_router(writing.router)
    app.include_router(client_crm.router)

elif GPT_MODE == "ops_team":
    from tyro_gateway.routers import client_crm, strategy
    app.include_router(client_crm.router)
    app.include_router(strategy.router)



# ✅ Step 5: 同步 repo 狀態（供 GPT 使用）
PROJECT_STATE = project_loader.sync_project()
print(f"📂 Loaded Files: {PROJECT_STATE['loaded']}")
for path in PROJECT_STATE["sample"]:
    print("  -", path)

# ✅ Step 6: 儲存目前專案快照（存入 logs）
try:
    os.makedirs("logs", exist_ok=True)
    with open("logs/project_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(PROJECT_STATE, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"⚠️ Failed to write snapshot log: {e}")

# ✅ Step 7: 健康檢查 + 狀態查詢 API
@app.get("/api/dev/project_status")
def get_project_state():
    return {
        "mode": GPT_MODE,
        "project": PROJECT_STATE
    }

@app.get("/")
def read_root():
    return {"message": f"Hello from TYRO Gateway — Mode: {GPT_MODE}"}
