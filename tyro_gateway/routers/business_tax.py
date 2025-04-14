# ✅ tyro_gateway/routers/business_tax.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal
from pydantic import BaseModel

from tyro_gateway.models.business_tax import BusinessTax
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

class BusinessTaxActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: BusinessTax

@router.post(
    "/business-tax",
    tags=["Business Tax"],
    summary="Create or query a business tax record",
    response_model=Dict[str, Any]
)
def handle_business_tax(
    request: Request,
    payload: BusinessTaxActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"BusinessTax::{action}",
        endpoint="/business-tax",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("business_tax", data)
        return create_record_if_not_exists("2.5", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.5", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Business Tax"
    }
