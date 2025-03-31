from fastapi import APIRouter
from notion_client import create_record
from models.investment import StockStrategy
from models.investment import OptionStrategy
from models.investment import RealEstate

router = APIRouter()

@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategy):
    return create_record("4.1", data.dict())

@router.post("/add-options-play")
def add_options_play(data: OptionStrategy):
    return create_record("4.2", data.dict())

@router.post("/add-real-estate")
def add_real_estate(data: RealEstate):
    return create_record("4.3", data.dict())

