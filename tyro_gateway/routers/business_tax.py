# tyro_gateway/routers/business_tax.py

from fastapi import APIRouter, Request
from tyro_gateway.models.business_tax import BusinessTax
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 3.2 Business Tax - CREATE
@router.post("/add-business-tax")
def add_business_tax(data: BusinessTax, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("3.2", data.dict())
    log_api_trigger(
        action_name="Add Business Tax",
        endpoint="/add-business-tax",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 3.2 Business Tax - QUERY
@router.get("/business-tax-records")
def list_business_tax(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("3.2", page_size=limit)
    log_api_trigger(
        action_name="List Business Tax",
        endpoint="/business-tax-records",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

