# tyro_gateway/routers/retailer_crm.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 3.2 Retailer CRM
@router.post("/retailer-crm")
def handle_retailer_crm(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

    log_api_trigger(
        action_name=f"RetailerCRM::{action}",
        endpoint="/retailer-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        return create_record("3.2", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("3.2", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Retailer CRM"
    }
