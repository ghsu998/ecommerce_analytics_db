# tyro_gateway/routers/strategy.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.strategy import Strategy

router = APIRouter()

# 6.1 Strategy Master - CREATE
@router.post("/add-strategy")
def add_strategy(data: Strategy):
    return create_record("6.1", data.dict())

# 6.1 Strategy Master - QUERY
@router.get("/strategies")
def list_strategies(limit: int = 10):
    return query_records("6.1", page_size=limit)

