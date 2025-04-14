# ✅ tyro_gateway/routers/email_identity.py（最終範例）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal
from pydantic import BaseModel

from tyro_gateway.models.email_identity import EmailIdentity  # ✅ 重用 model schema
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

# ✅ 統一 action schema（直接使用原始資料結構）
class EmailIdentityActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: EmailIdentity

@router.post(
    "/email-identity",
    tags=["Email Identity"],
    summary="Create or query an email identity profile",
    response_model=Dict[str, Any]
)
def handle_email_identity(
    request: Request,
    payload: EmailIdentityActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"EmailIdentity::{action}",
        endpoint="/email-identity",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("email_identity", data)
        return create_record_if_not_exists("2.1", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.1", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Email Identity"
    }
