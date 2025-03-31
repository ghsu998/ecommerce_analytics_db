from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.strategy import Strategy

router = APIRouter()

@router.post("/add-strategy")
def add_strategy(data: Strategy):
    return create_record("6.1", data.dict())