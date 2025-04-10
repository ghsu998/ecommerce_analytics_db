# tyro_gateway/routers/email_identity.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.1 Email Identity 
@router.post("/email-identity")
def handle_email_identity(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

    log_api_trigger(
        action_name=f"EmailIdentity::{action}",
        endpoint="/email-identity",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        return create_record("2.1", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.1", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Email Identity"
    }



