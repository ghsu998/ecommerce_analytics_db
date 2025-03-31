from fastapi import APIRouter
from models.execution import ApiTrigger
from notion_client import create_record

router = APIRouter()

@router.post("/add-api-trigger")
def add_api_trigger(data: ApiTrigger):
    return create_record("5.1", data.dict())
