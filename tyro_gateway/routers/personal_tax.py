# ✅ tyro_gateway/routers/personal_tax.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.personal_tax import PersonalTax
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

class PersonalTaxActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: PersonalTax

class PersonalTaxResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[PersonalTax] = None
    results: Optional[List[PersonalTax]] = None
    notion_id: Optional[str] = None

@router.post(
    "/personal-tax",
    tags=["Personal Tax"],
    summary="Create or query a personal tax record",
    response_model=PersonalTaxResponse
)
def handle_personal_tax(
    request: Request,
    payload: PersonalTaxActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"PersonalTax::{action}",
        endpoint="/personal-tax",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("personal_tax", data)
        result = create_record_if_not_exists("2.4", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, PersonalTax) if notion_data else None
        return PersonalTaxResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    elif action == "query":
        limit = data.get("limit", 10)
        status_code, response = query_records("2.4", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, PersonalTax) for n in notion_results
        ]
        return PersonalTaxResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    return PersonalTaxResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Personal Tax"
    )

