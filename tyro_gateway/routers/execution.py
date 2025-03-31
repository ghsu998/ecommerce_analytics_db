from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.api_trigger import APITrigger

router = APIRouter()

@router.post("/add-api-trigger-log")
def add_api_trigger(data: APITrigger):
    return create_record("5.1", data.dict())