# tyro_gateway/routers/personal_tax.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key


router = APIRouter()

# 📌 2.4 Personal Tax 
@router.post("/personal-tax")
def handle_personal_tax(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

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
        return create_record("2.4", data)


    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.4", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Personal Tax"
    }
