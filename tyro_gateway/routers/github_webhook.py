# tyro_gateway/routers/github_webhook.py

import os
from datetime import datetime
from fastapi import APIRouter, Request
import subprocess

router = APIRouter()

def log_webhook(message: str):
    log_dir = "/home/ubuntu/ecommerce_analytics_db/logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "github_webhook.log"), "a") as f:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

@router.post("/api/github_webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    ref = payload.get("ref")
    log_webhook(f"📩 Received webhook for ref: {ref}")

    if ref == "refs/heads/main":
        try:
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd="/home/ubuntu/ecommerce_analytics_db",
                check=True
            )
            subprocess.run(["pm2", "restart", "tyro-gateway"], check=True)
            log_webhook("✅ Pull + restart success")
            return {"status": "✅ Code updated & restarted."}
        except subprocess.CalledProcessError as e:
            log_webhook(f"❌ Error during deployment: {str(e)}")
            return {"status": "❌ Error during deployment", "details": str(e)}

    log_webhook(f"⏭ Skipped non-main push: {ref}")
    return {"status": "⏭ Skipped - not a push to main."}
