from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.api_trigger import ApiTriggerLog

router = APIRouter()

@router.post("/add-api-trigger-log")
def add_api_trigger(data: ApiTriggerLog):
    return create_record("5.1", data.dict())