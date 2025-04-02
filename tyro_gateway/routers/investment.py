# tyro_gateway/routers/investment.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.stock_strategy import StockStrategy
from tyro_gateway.models.options_strategy import OptionsStrategy
from tyro_gateway.models.real_estate import RealEstateEntry

router = APIRouter()

# 4.1 Stock Strategy - CREATE
@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategy):
    return create_record("4.1", data.dict())

# 4.2 Options Strategy - CREATE
@router.post("/add-options-strategy")
def add_options_strategy(data: OptionsStrategy):
    return create_record("4.2", data.dict())

# 4.3 Real Estate - CREATE
@router.post("/add-real-estate")
def add_real_estate(data: RealEstateEntry):
    return create_record("4.3", data.dict())

# 4.1 Stock Strategy - QUERY
@router.get("/stock-strategies")
def list_stock_strategies(limit: int = 10):
    return query_records("4.1", page_size=limit)

# 4.2 Options Strategy - QUERY
@router.get("/options-Strategys")
def list_options_strategys(limit: int = 10):
    return query_records("4.2", page_size=limit)

# 4.3 Real Estate - QUERY
@router.get("/real-estate")
def list_real_estate(limit: int = 10):
    return query_records("4.3", page_size=limit)
