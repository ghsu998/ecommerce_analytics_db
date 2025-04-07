# tyro_gateway/routers/__init__.py

from fastapi import APIRouter

# ✅ 匯入所有主功能模組 router
from tyro_gateway.routers.career import router as career_router
from tyro_gateway.routers.tax import router as tax_router
from tyro_gateway.routers.investment import router as investment_router
from tyro_gateway.routers.writing import router as writing_router
from tyro_gateway.routers.api_trigger import router as api_trigger_router
from tyro_gateway.routers.strategy import router as strategy_router
from tyro_gateway.routers.repo_docs import router as repo_docs_router

# ✅ 建立主 router 入口點，供 dev 模式統一測試使用
router = APIRouter()

# ✅ 統一整合所有模組
router.include_router(career_router)
router.include_router(tax_router)
router.include_router(investment_router)
router.include_router(writing_router)
router.include_router(api_trigger_router)
router.include_router(strategy_router)
router.include_router(repo_docs_router)  # 📘 Git repo 代碼分析功能

# 💡 此 router 僅在 GPT_MODE = dev 時載入，可一次性測試所有 endpoint
