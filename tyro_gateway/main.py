# tyro_gateway/main.py

from fastapi import FastAPI
from tyro_gateway.routers import router  # ✅ 匯入你的主要 router group（這邊需確保 routers/__init__.py 存在）
from tyro_gateway.routers import github_webhook  # ✅ 匯入 webhook 處理模組
from tyro_gateway.utils import github_utils  # ✅ 修正這行
from tyro_gateway.utils import project_loader

# ✅ 初始化 FastAPI 應用
app = FastAPI()

# ✅ 根路由，用來測試 API 是否正常啟動
@app.get("/")
def read_root():
    return {"message": "Hello from TYRO Gateway"}

# ✅ 載入主系統內的所有功能路由（career、tax、investment...）
app.include_router(router)

# ✅ 專門處理 GitHub Webhook 的路由（例如 git pull + restart）
app.include_router(github_webhook.router)

# ✅ 提供 latest commit endpoint
app.include_router(github_utils.router)
