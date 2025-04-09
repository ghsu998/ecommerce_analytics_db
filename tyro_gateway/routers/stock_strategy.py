# tyro_gateway/routers/stock_strategy.py

from fastapi import APIRouter, Request
from tyro_gateway.models.stock_strategy import StockStrategy
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.6 Stock Strategy - CREATE
@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategy, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.6", data.dict())
    log_api_trigger(
        action_name="Add Stock Strategy",
        endpoint="/add-stock-strategy",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.6 Stock Strategy - QUERY
@router.get("/stock-strategies")
def list_stock_strategies(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.6", page_size=limit)
    log_api_trigger(
        action_name="List Stock Strategies",
        endpoint="/stock-strategies",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res
