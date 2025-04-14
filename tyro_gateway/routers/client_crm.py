# ✅ tyro_gateway/routers/client_crm.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal
from pydantic import BaseModel

from tyro_gateway.models.client_crm import ClientCRM
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

class ClientCRMActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: ClientCRM

@router.post(
    "/client-crm",
    tags=["Client CRM"],
    summary="Create or query a client CRM record",
    response_model=Dict[str, Any]
)
def handle_client_crm(
    request: Request,
    payload: ClientCRMActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"ClientCRM::{action}",
        endpoint="/client-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("client_crm", data)
        return create_record_if_not_exists("3.1", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("3.1", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Client CRM"
    }
