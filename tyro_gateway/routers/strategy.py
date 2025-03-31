from fastapi import APIRouter
from models.strategy import Strategy
from notion_client import create_record

router = APIRouter()

@router.post("/add-strategy")
def add_strategy(data: Strategy):
    return create_record("6.1", data.dict())
