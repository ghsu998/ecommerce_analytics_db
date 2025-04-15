# ✅ tyro_gateway/routers/client_crm.py（GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.client_crm import ClientCRM
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ 請求格式定義
class ClientCRMActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: ClientCRM

# ✅ 回傳格式定義
class ClientCRMResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[ClientCRM] = None
    results: Optional[List[ClientCRM]] = None
    notion_id: Optional[str] = None

@router.post(
    "/client-crm",
    tags=["Client CRM"],
    summary="Create or query a client CRM record",
    response_model=ClientCRMResponse
)
def handle_client_crm(
    request: Request,
    payload: ClientCRMActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    # ✅ 操作紀錄
    log_api_trigger(
        action_name=f"ClientCRM::{action}",
        endpoint="/client-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立紀錄流程
    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("client_crm", data)
        result = create_record_if_not_exists("3.1", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, ClientCRM) if notion_data else None
        return ClientCRMResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢流程（加入 limit 防呆）
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("3.1", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, ClientCRM) for n in notion_results
        ]
        return ClientCRMResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback for unknown action
    return ClientCRMResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Client CRM"
    )
