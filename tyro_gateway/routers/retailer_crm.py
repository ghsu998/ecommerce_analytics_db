# ✅ tyro_gateway/routers/retailer_crm.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal
from pydantic import BaseModel

from tyro_gateway.models.retailer_crm import RetailerCRM
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

class RetailerCRMActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: RetailerCRM

@router.post(
    "/retailer-crm",
    tags=["Retailer CRM"],
    summary="Create or query a retailer CRM record",
    response_model=Dict[str, Any]
)
def handle_retailer_crm(
    request: Request,
    payload: RetailerCRMActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"RetailerCRM::{action}",
        endpoint="/retailer-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("retailer_crm", data)
        return create_record_if_not_exists("3.2", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("3.2", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Retailer CRM"
    }