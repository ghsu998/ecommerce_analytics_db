# ✅ tyro_gateway/routers/business_tax.py（支援獨立 query schema）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal, Optional, Union
from pydantic import BaseModel

from tyro_gateway.models.business_tax import BusinessTax
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

# ✅ 拆開 schema
class BusinessTaxCreateInput(BusinessTax):
    pass

class BusinessTaxQueryInput(BaseModel):
    limit: Optional[int] = 10

class BusinessTaxActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: Union[BusinessTaxCreateInput, BusinessTaxQueryInput]

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

    log_api_trigger(
        action_name=f"BusinessTax::{action}",
        endpoint="/business-tax",
        data_summary=payload.data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        data = payload.data.dict()
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("business_tax", data)
        return create_record_if_not_exists("2.5", data)

    elif action == "query":
        limit = getattr(payload.data, "limit", 10)
        return query_records("2.5", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Business Tax"
    }
