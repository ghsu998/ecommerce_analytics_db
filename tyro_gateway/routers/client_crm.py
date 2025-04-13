# tyro_gateway/routers/client_crm.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import create_record_if_not_exists


router = APIRouter()

# 📌 3.1 Client CRM
@router.post("/client-crm")
def handle_client_crm(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

    log_api_trigger(
        action_name=f"ClientCRM::{action}",
        endpoint="/client-crm",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("client_crm", data)
        return create_record_if_not_exists("3.1", data)


    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("3.1", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Client CRM"
    }
