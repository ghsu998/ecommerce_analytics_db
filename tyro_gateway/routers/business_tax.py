# ✅ tyro_gateway/routers/business_tax.py（支援獨立 query schema）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional, Union
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

# ✅ 查詢用 schema（只需 limit）
class BusinessTaxQueryInput(BaseModel):
    limit: Optional[int] = 10

# ✅ 建立 / 查詢請求共用包裝格式
class BusinessTaxActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: Union[BusinessTax, BusinessTaxQueryInput]

# ✅ ✨ 回傳格式標準化（與其他 router 一致）
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

    log_api_trigger(
        action_name=f"BusinessTax::{action}",
        endpoint="/business-tax",
        data_summary=payload.data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立流程
    if action == "create":
        data = payload.data.dict()
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

    # ✅ 查詢流程
    elif action == "query":
        try:
            raw_limit = getattr(payload.data, "limit", 10)
            limit = max(1, min(int(raw_limit), 100))
        except (ValueError, TypeError):
            limit = 10

        status_code, response = query_records("2.5", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, BusinessTax) for n in notion_results
        ]

        return BusinessTaxResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ fallback for unknown action
    return BusinessTaxResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Business Tax"
    )
