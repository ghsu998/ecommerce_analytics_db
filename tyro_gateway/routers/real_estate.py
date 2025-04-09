# tyro_gateway/routers/real_estate.py

from fastapi import APIRouter, Request
from tyro_gateway.models.real_estate import RealEstate
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.8 Real Estate - CREATE
@router.post("/add-real-estate")
def add_real_estate(data: RealEstate, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.8", data.dict())
    log_api_trigger(
        action_name="Add Real Estate",
        endpoint="/add-real-estate",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.8 Real Estate - QUERY
@router.get("/real-estates")
def list_real_estates(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.8", page_size=limit)
    log_api_trigger(
        action_name="List Real Estates",
        endpoint="/real-estates",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

