# tyro_gateway/routers/api_triggers.py

from fastapi import APIRouter, Request
from tyro_gateway.utils.notion_client import query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 5.1 API Trigger Log - QUERY
@router.get("/api-triggers")
def list_api_triggers(limit: int = 20, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("5.1", page_size=limit)
    log_api_trigger(
        action_name="List API Triggers",
        endpoint="/api-triggers",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res


