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
app = FastAPI(
    title="TYRO Gateway API",
    description="Unified API Gateway for Notion-integrated GPT Plugin",
    version="1.0.0"
)
print(f"🧠 GPT Gateway 啟動模式：{GPT_MODE}")

# ✅ Step 3: 掛載常駐 router（與 GPT 模式無關）
from tyro_gateway.routers import github_webhook, repo_docs, api_trigger
app.include_router(github_webhook.router)
app.include_router(repo_docs.router)
app.include_router(api_trigger.router)

# ✅ Step 4: 根據 GPT_MODE 載入 routers
from tyro_gateway.routers import (
    strategy, job_application, business_tax, client_crm,
    email_identity, options_strategy, personal_tax, real_estate,
    resume_version, stock_strategy, retailer_crm
)

router_registry = {
    "email_identity":     (email_identity,     "/email-identity",     ["Email Identity"]),
    "job_application":    (job_application,    "/job-application",    ["Job Application"]),
    "resume_version":     (resume_version,     "/resume-version",     ["Resume Version"]),
    "personal_tax":       (personal_tax,       "/personal-tax",       ["Personal Tax"]),
    "strategy":           (strategy,           "/strategy",           ["Strategy"]),
    "business_tax":       (business_tax,       "/business-tax",       ["Business Tax"]),
    "stock_strategy":     (stock_strategy,     "/stock-strategy",     ["Stock Strategy"]),
    "options_strategy":   (options_strategy,   "/options-strategy",   ["Options Strategy"]),
    "real_estate":        (real_estate,        "/real-estate",        ["Real Estate"]),
    "client_crm":         (client_crm,         "/client-crm",         ["Client CRM"]),
    "retailer_crm":       (retailer_crm,       "/retailer-crm",       ["Retailer CRM"]),
}

if GPT_MODE in ["development", "root user"]:
    enabled_keys = list(router_registry.keys())
elif GPT_MODE == "team user":
    enabled_keys = ["client_crm", "retailer_crm"]
else:
    enabled_keys = []

for key in enabled_keys:
    try:
        module, prefix, tags = router_registry[key]
        app.include_router(module.router, prefix=prefix, tags=tags)
    except KeyError:
        print(f"⚠️ Router key not found: {key}")

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
