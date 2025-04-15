# ✅ tyro_gateway/routers/options_strategy.py（重構為 GPT Plugin 標準格式）
from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.options_strategy import OptionsStrategy
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ 請求格式定義
class OptionsStrategyActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: OptionsStrategy

# ✅ 回傳格式定義
class OptionsStrategyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[OptionsStrategy] = None
    results: Optional[List[OptionsStrategy]] = None
    notion_id: Optional[str] = None

@router.post(
    "/options-strategy",
    tags=["Options Strategy"],
    summary="Create or query an options strategy record",
    response_model=OptionsStrategyResponse
)
def handle_options_strategy(
    request: Request,
    payload: OptionsStrategyActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    # ✅ 操作紀錄
    log_api_trigger(
        action_name=f"OptionsStrategy::{action}",
        endpoint="/options-strategy",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立流程
    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("options_strategy", data)
        result = create_record_if_not_exists("2.7", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, OptionsStrategy) if notion_data else None
        return OptionsStrategyResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢流程（加上 limit 防呆）
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))  # 限制 1~100
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("2.7", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, OptionsStrategy) for n in notion_results
        ]
        return OptionsStrategyResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback
    return OptionsStrategyResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Options Strategy"
    )
