# ✅ tyro_gateway/routers/retailer_crm.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.retailer_crm import RetailerCRM
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ 請求格式
class RetailerCRMActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: RetailerCRM

# ✅ 回傳格式
class RetailerCRMResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[RetailerCRM] = None
    results: Optional[List[RetailerCRM]] = None
    notion_id: Optional[str] = None

@router.post(
    "/retailer-crm",
    tags=["Retailer CRM"],
    summary="Create or query a retailer CRM record",
    response_model=RetailerCRMResponse
)
def handle_retailer_crm(
    request: Request,
    payload: RetailerCRMActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    # ✅ 記錄 log
    log_api_trigger(
        action_name=f"RetailerCRM::{action}",
        endpoint="/retailer-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立資料
    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("retailer_crm", data)
        result = create_record_if_not_exists("3.2", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, RetailerCRM) if notion_data else None
        return RetailerCRMResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢資料（加入 limit 限制）
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("3.2", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, RetailerCRM) for n in notion_results
        ]
        return RetailerCRMResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback for unknown action
    return RetailerCRMResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Retailer CRM"
    )
