# tyro_gateway/routers/real_estate.py

from fastapi import APIRouter, Request, Body
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.8 Real Estate
@router.post("/real-estate")
def handle_real_estate(
    request: Request,
    action: str = Body(..., embed=True),
    data: dict = Body(default={})
):
    user_identity = request.headers.get("x-user-identity", "chat")

    log_api_trigger(
        action_name=f"RealEstate::{action}",
        endpoint="/real-estate",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        return create_record("2.8", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.8", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Real Estate"
    }
