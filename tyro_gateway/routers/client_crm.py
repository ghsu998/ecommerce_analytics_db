# tyro_gateway/routers/client_crm.py

from fastapi import APIRouter, Request
from tyro_gateway.models.client_crm import ClientCRM
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 3.1 Client CRM - CREATE
@router.post("/add-client-crm")
def add_client_crm(data: ClientCRM, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("3.1", data.dict())
    log_api_trigger(
        action_name="Add Client CRM",
        endpoint="/add-client-crm",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 3.1 Client CRM - QUERY
@router.get("/client-crm")
def list_client_crm(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("3.1", page_size=limit)
    log_api_trigger(
        action_name="List Client CRM",
        endpoint="/client-crm",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

