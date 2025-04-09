# tyro_gateway/routers/email_identity.py

from fastapi import APIRouter, Request
from tyro_gateway.models.email_identity import EmailIdentity
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.1 Email Identity - CREATE
@router.post("/add-email-identity")
def add_email_identity(data: EmailIdentity, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.1", data.dict())
    log_api_trigger(
        action_name="Add Email Identity",
        endpoint="/add-email-identity",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.1 Email Identity - QUERY
@router.get("/email-identities")
def list_email_identities(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.1", page_size=limit)
    log_api_trigger(
        action_name="List Email Identities",
        endpoint="/email-identities",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res



