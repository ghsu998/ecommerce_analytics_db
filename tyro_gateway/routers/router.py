# tyro_gateway/routers/router.py

from fastapi import APIRouter

from tyro_gateway.routers import (
    career,
    tax,
    investment,
    strategy,
    writing,
    execution,
)

router = APIRouter()

# ✅ 主功能 API modules
router.include_router(career.router, prefix="/api/career", tags=["career"])
router.include_router(tax.router, prefix="/api/tax", tags=["tax"])
router.include_router(investment.router, prefix="/api/investment", tags=["investment"])
router.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
router.include_router(writing.router, prefix="/api/writing", tags=["writing"])
router.include_router(execution.router, prefix="/api/execution", tags=["execution"])
