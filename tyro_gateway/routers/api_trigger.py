# tyro_gateway/routers/execution.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.api_trigger import APITrigger

router = APIRouter()

# 5.1 API Trigger Log - CREATE
@router.post("/add-api-trigger-log")
def add_api_trigger(data: APITrigger):
    return create_record("5.1", data.dict())

# 5.1 API Trigger Log - QUERY
@router.get("/api-trigger-logs")
def list_api_triggers(limit: int = 10):
    return query_records("5.1", page_size=limit)

