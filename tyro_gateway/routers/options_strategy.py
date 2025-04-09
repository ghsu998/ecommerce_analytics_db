# tyro_gateway/routers/options_strategy.py

from fastapi import APIRouter, Request
from tyro_gateway.models.options_strategy import OptionsStrategy
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.7 Options Strategy - CREATE
@router.post("/add-options-strategy")
def add_options_strategy(data: OptionsStrategy, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.7", data.dict())
    log_api_trigger(
        action_name="Add Options Strategy",
        endpoint="/add-options-strategy",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.7 Options Strategy - QUERY
@router.get("/options-strategies")
def list_options_strategies(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.7", page_size=limit)
    log_api_trigger(
        action_name="List Options Strategies",
        endpoint="/options-strategies",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res
