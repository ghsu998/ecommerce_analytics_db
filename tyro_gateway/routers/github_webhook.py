# tyro_gateway/routers/github_webhook.py

from fastapi import APIRouter, Request
import subprocess

router = APIRouter()

@router.post("/api/github_webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    # 若是 main 分支 push
    if payload.get("ref") == "refs/heads/main":
        try:
            # 對整個 repo 做 git pull
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd="/home/ubuntu/ecommerce_analytics_db",
                check=True
            )
            subprocess.run(["pm2", "restart", "tyro-gateway"], check=True)
            return {"status": "✅ updated & restarted"}
        except subprocess.CalledProcessError as e:
            return {"status": "❌ error", "details": str(e)}

    return {"status": "skipped"}
