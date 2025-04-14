# ✅ tyro_gateway/routers/email_identity.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.email_identity import EmailIdentity
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

class EmailIdentityActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: EmailIdentity

class EmailIdentityResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[EmailIdentity] = None
    results: Optional[List[EmailIdentity]] = None
    notion_id: Optional[str] = None

@router.post(
    "/email-identity",
    tags=["Email Identity"],
    summary="Create or query an email identity profile",
    response_model=EmailIdentityResponse
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
        result = create_record_if_not_exists("2.1", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, EmailIdentity) if notion_data else None
        return EmailIdentityResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    elif action == "query":
        limit = data.get("limit", 10)
        status_code, response = query_records("2.1", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, EmailIdentity) for n in notion_results
        ]
        return EmailIdentityResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    return EmailIdentityResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Email Identity"
    )
