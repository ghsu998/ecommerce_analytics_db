import os
from datetime import datetime
from fastapi import APIRouter, Request, BackgroundTasks
import subprocess

router = APIRouter()

def log_webhook(message: str):
    log_dir = "/home/ubuntu/ecommerce_analytics_db/logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "github_webhook.log"), "a") as f:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def restart_pm2():
    try:
        subprocess.run(["pm2", "restart", "tyro-gateway"], check=True)
        log_webhook("✅ Restarted tyro-gateway in background.")
    except subprocess.CalledProcessError as e:
        log_webhook(f"❌ Restart error: {str(e)}")

@router.post("/api/github_webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
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
            log_webhook("✅ Pulled latest main branch.")
            background_tasks.add_task(restart_pm2)
            return {"status": "✅ Pulled latest code. Restart scheduled."}
        except subprocess.CalledProcessError as e:
            log_webhook(f"❌ Pull error: {str(e)}")
            return {"status": "❌ Pull error", "details": str(e)}

    log_webhook(f"⏭ Skipped non-main push: {ref}")
    return {"status": "⏭ Skipped - not a push to main."}