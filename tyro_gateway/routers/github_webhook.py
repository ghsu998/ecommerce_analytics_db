# tyro_gateway/routers/github_webhook.py

from fastapi import APIRouter, Request
import subprocess

router = APIRouter()

@router.post("/api/github_webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    # 僅監聽 main branch 的 push event
    if payload.get("ref") == "refs/heads/main":
        try:
            # ✅ 拉取最新代碼
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd="/home/ubuntu/ecommerce_analytics_db",  # ← 改為你實際的專案資料夾
                check=True
            )

            # ✅ 重新啟動應用服務
            subprocess.run(["pm2", "restart", "tyro-gateway"], check=True)

            return {"status": "✅ Code updated & service restarted."}

        except subprocess.CalledProcessError as e:
            return {"status": "❌ Error during deployment", "details": str(e)}

    return {"status": "⏭ Skipped - not a push to main."}
