# tyro_gateway/routers/github_webhook.py

import os
import subprocess
from datetime import datetime
from fastapi import APIRouter, Request

router = APIRouter()

# ✅ 記錄 webhook 行為到 logs/github_webhook.log
def log_webhook(message: str):
    log_dir = "/home/ubuntu/ecommerce_analytics_db/logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "github_webhook.log"), "a") as f:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


@router.post("/api/github_webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    # ✅ 僅監聽 main 分支的 push
    if payload.get("ref") == "refs/heads/main":
        try:
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd="/home/ubuntu/ecommerce_analytics_db",
                check=True
            )
            subprocess.run(["pm2", "restart", "tyro-gateway"], check=True)
            log_webhook("✅ Pull + restart success")
            return {"status": "✅ Code updated & service restarted."}

        except subprocess.CalledProcessError as e:
            log_webhook(f"❌ Pull failed: {str(e)}")
            return {"status": "❌ Error during deployment", "details": str(e)}

    # 非 main 分支
    log_webhook(f"⏭ Skipped ref: {payload.get('ref')}")
    return {"status": "⏭ Skipped - not a push to main."}
