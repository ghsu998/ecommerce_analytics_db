# tyro_gateway/main.py

import os
import json
import project_loader
from fastapi import FastAPI
from dotenv import load_dotenv
from tyro_gateway.env_loader import get_gpt_mode

# ✅ Step 1: 載入環境變數與 GPT 模式
load_dotenv()
GPT_MODE = get_gpt_mode()

# ✅ Step 2: 初始化 FastAPI 應用
app = FastAPI()
print(f"🧠 GPT Gateway 啟動模式：{GPT_MODE}")

# ✅ Step 3: 掛載常駐 router（與 GPT 模式無關）
from tyro_gateway.routers import github_webhook, repo_docs, api_trigger
app.include_router(github_webhook.router)
app.include_router(repo_docs.router)
app.include_router(api_trigger.router)

# ✅ Step 4: 根據身份模式載入 router
from tyro_gateway.routers import (
    strategy, job_application, business_tax, client_crm,
    email_identity, options_strategy, personal_tax, real_estate,
    resume_version, stock_strategy, retailer_crm
)

if GPT_MODE == "dev":
    routers = [
        strategy, job_application, business_tax, client_crm,
        email_identity, options_strategy, personal_tax, real_estate,
        resume_version, stock_strategy, retailer_crm
    ]
elif GPT_MODE == "ops_root":
    routers = [
        strategy, email_identity, resume_version, job_application,
        personal_tax, business_tax, client_crm, real_estate, stock_strategy
    ]
elif GPT_MODE == "ops_team":
    routers = [client_crm, retailer_crm]
else:
    routers = []

for r in routers:
    app.include_router(r.router)

# ✅ Step 5: 掃描並記錄專案狀態
PROJECT_STATE = project_loader.sync_project()
print(f"📂 Loaded Files: {PROJECT_STATE['loaded']}")
for path in PROJECT_STATE["sample"]:
    print("  -", path)

try:
    os.makedirs("logs", exist_ok=True)
    with open("logs/project_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(PROJECT_STATE, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"⚠️ Failed to write snapshot log: {e}")

# ✅ Step 6: 健康檢查 API
@app.get("/api/dev/project_status")
def get_project_state():
    return {
        "mode": GPT_MODE,
        "project": PROJECT_STATE
    }

@app.get("/")
def read_root():
    return {"message": f"Hello from TYRO Gateway — Mode: {GPT_MODE}"}
