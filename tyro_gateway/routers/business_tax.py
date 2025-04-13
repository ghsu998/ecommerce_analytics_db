# tyro_gateway/routers/business_tax.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import create_record_if_not_exists


router = APIRouter()

# 📌 2.5 Business Tax
@router.post("/business-tax")
def handle_business_tax(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

    log_api_trigger(
        action_name=f"BusinessTax::{action}",
        endpoint="/business-tax",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("business_tax", data)
        return create_record_if_not_exists("2.5", data)


    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.5", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Business Tax"
    }
