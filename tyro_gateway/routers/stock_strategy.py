# tyro_gateway/routers/investment.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.stock_strategy import StockStrategy


router = APIRouter()

# 4.1 Stock Strategy - CREATE
@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategy):
    return create_record("4.1", data.dict())




# 4.1 Stock Strategy - QUERY
@router.get("/stock-strategies")
def list_stock_strategies(limit: int = 10):
    return query_records("4.1", page_size=limit)

