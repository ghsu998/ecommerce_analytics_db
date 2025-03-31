from fastapi import APIRouter

from tyro_gateway.routers.career import router as career_router
from tyro_gateway.routers.tax import router as tax_router
from tyro_gateway.routers.investment import router as investment_router
from tyro_gateway.routers.writing import router as writing_router
from tyro_gateway.routers.execution import router as execution_router
from tyro_gateway.routers.strategy import router as strategy_router

router = APIRouter()

router.include_router(career_router)
router.include_router(tax_router)
router.include_router(investment_router)
router.include_router(writing_router)
router.include_router(execution_router)
router.include_router(strategy_router)
