# tyro_gateway/routers/__init__.py

from fastapi import APIRouter

# ✅ 匯入所有模組化 router（每個對應 Notion DB 一對一）
from tyro_gateway.routers.api_trigger import router as api_trigger_router
from tyro_gateway.routers.business_tax import router as business_tax_router
from tyro_gateway.routers.client_crm import router as client_crm_router
from tyro_gateway.routers.email_identity import router as email_identity_router
from tyro_gateway.routers.job_application import router as job_application_router
from tyro_gateway.routers.options_strategy import router as options_strategy_router
from tyro_gateway.routers.personal_tax import router as personal_tax_router
from tyro_gateway.routers.real_estate import router as real_estate_router
from tyro_gateway.routers.resume_version import router as resume_version_router
from tyro_gateway.routers.stock_strategy import router as stock_strategy_router
from tyro_gateway.routers.strategy import router as strategy_router
from tyro_gateway.routers.repo_docs import router as repo_docs_router  # ✅ Git repo 分析

# ✅ 建立 router 入口點
router = APIRouter()

# ✅ 統一註冊所有模組 router
router.include_router(api_trigger_router)
router.include_router(business_tax_router)
router.include_router(client_crm_router)
router.include_router(email_identity_router)
router.include_router(job_application_router)
router.include_router(options_strategy_router)
router.include_router(personal_tax_router)
router.include_router(real_estate_router)
router.include_router(resume_version_router)
router.include_router(stock_strategy_router)
router.include_router(strategy_router)
router.include_router(repo_docs_router)
