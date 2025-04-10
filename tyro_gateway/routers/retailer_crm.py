# tyro_gateway/routers/retailer_crm.py

from fastapi import APIRouter, Request
from tyro_gateway.models.retailer_crm import RetailerCRM
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 3.2 retailer CRM - CREATE
@router.post("/add-retailer-crm")
def add_retailer_crm(data: RetailerCRM, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("3.2", data.dict())
    log_api_trigger(
        action_name="Add retailer CRM",
        endpoint="/add-retailer-crm",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 3.2 retailer CRM - QUERY
@router.get("/retailer-crm")
def list_retailer_crm(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("3.2", page_size=limit)
    log_api_trigger(
        action_name="List retailer CRM",
        endpoint="/retailer-crm",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

