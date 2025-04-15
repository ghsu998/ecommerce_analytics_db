# ✅ tyro_gateway/routers/strategy.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.strategy import Strategy
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ 請求格式
class StrategyActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: Strategy

# ✅ 統一回傳格式
class StrategyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[Strategy] = None
    results: Optional[List[Strategy]] = None
    notion_id: Optional[str] = None

@router.post(
    "/strategy",
    tags=["Strategy"],
    summary="Create or query a strategy record",
    response_model=StrategyResponse
)
def handle_strategy(
    request: Request,
    payload: StrategyActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    # ✅ 寫入 API log
    log_api_trigger(
        action_name=f"Strategy::{action}",
        endpoint="/strategy",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立策略紀錄
    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("strategy", data)
        result = create_record_if_not_exists("2.9", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, Strategy) if notion_data else None
        return StrategyResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢資料流程（加入 limit 防呆）
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("2.9", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, Strategy) for n in notion_results
        ]
        return StrategyResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback
    return StrategyResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Strategy"
    )
