# ✅ tyro_gateway/routers/stock_strategy.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.stock_strategy import StockStrategy
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ 請求格式
class StockStrategyActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: StockStrategy

# ✅ 回傳格式（與其他 router 一致）
class StockStrategyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[StockStrategy] = None
    results: Optional[List[StockStrategy]] = None
    notion_id: Optional[str] = None

@router.post(
    "/stock-strategy",
    tags=["Stock Strategy"],
    summary="Create or query a stock strategy record",
    response_model=StockStrategyResponse
)
def handle_stock_strategy(
    request: Request,
    payload: StockStrategyActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    # ✅ 紀錄操作
    log_api_trigger(
        action_name=f"StockStrategy::{action}",
        endpoint="/stock-strategy",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立紀錄流程
    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("stock_strategy", data)

        result = create_record_if_not_exists("2.6", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, StockStrategy) if notion_data else None

        return StockStrategyResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢資料（加 limit 防呆）
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("2.6", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, StockStrategy) for n in notion_results
        ]

        return StockStrategyResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback
    return StockStrategyResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Stock Strategy"
    )
