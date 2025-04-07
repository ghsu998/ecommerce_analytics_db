# tyro_gateway/routers/personal_tax.py

from fastapi import APIRouter, Request
from tyro_gateway.models.personal_tax import PersonalTax
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 3.1 Personal Tax - CREATE
@router.post("/add-personal-tax")
def add_personal_tax(data: PersonalTax, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("3.1", data.dict())
    log_api_trigger(
        action_name="Add Personal Tax",
        endpoint="/add-personal-tax",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 3.1 Personal Tax - QUERY
@router.get("/personal-tax-records")
def list_personal_tax(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("3.1", page_size=limit)
    log_api_trigger(
        action_name="List Personal Tax",
        endpoint="/personal-tax-records",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

