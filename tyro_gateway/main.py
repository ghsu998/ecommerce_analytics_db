import os
import json
import project_loader
from fastapi import FastAPI
from dotenv import load_dotenv
from tyro_gateway.env_loader import get_gpt_mode

# Step 1: Load .env and GPT Mode
load_dotenv()
GPT_MODE = get_gpt_mode()

# Step 2: Initialize FastAPI
app = FastAPI()
print(f"🧠 GPT Gateway 啟動模式：{GPT_MODE}")

# Step 3: Common routers (always loaded)
from tyro_gateway.routers import github_webhook, repo_docs
app.include_router(github_webhook.router)
app.include_router(repo_docs.router)

# Step 4: Dynamically load routers based on mode
from tyro_gateway.routers import (
    strategy, job_application, business_tax, client_crm,
    email_identity, options_strategy, personal_tax, real_estate,
    resume_version, stock_strategy, api_trigger, retailer_crm  # ✅ 加入 retailer_crm
)

if GPT_MODE == "dev":
    routers = [
        strategy, job_application, business_tax, client_crm,
        email_identity, options_strategy, personal_tax, real_estate,
        resume_version, stock_strategy, api_trigger,
        retailer_crm  # ✅ 加入到 dev 模式
    ]
elif GPT_MODE == "ops_root":
    routers = [
        strategy, email_identity, resume_version, job_application,
        personal_tax, business_tax, client_crm, real_estate, stock_strategy
    ]
elif GPT_MODE == "ops_team":
    routers = [strategy, client_crm]
else:
    routers = []

for r in routers:
    app.include_router(r.router)

# Step 5: Load and snapshot project structure
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

# Step 6: Health check & project status
@app.get("/api/dev/project_status")
def get_project_state():
    return {
        "mode": GPT_MODE,
        "project": PROJECT_STATE
    }

@app.get("/")
def read_root():
    return {"message": f"Hello from TYRO Gateway — Mode: {GPT_MODE}"}
