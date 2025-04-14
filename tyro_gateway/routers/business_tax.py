# ✅ tyro_gateway/routers/business_tax.py（GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.business_tax import BusinessTax
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

class BusinessTaxActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: BusinessTax

class BusinessTaxResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[BusinessTax] = None
    results: Optional[List[BusinessTax]] = None
    notion_id: Optional[str] = None

@router.post(
    "/business-tax",
    tags=["Business Tax"],
    summary="Create or query a business tax record",
    response_model=BusinessTaxResponse
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
        result = create_record_if_not_exists("2.5", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, BusinessTax) if notion_data else None
        return BusinessTaxResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    elif action == "query":
        limit = data.get("limit", 10)
        status_code, response = query_records("2.5", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, BusinessTax) for n in notion_results
        ]
        return BusinessTaxResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    return BusinessTaxResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Business Tax"
    )
