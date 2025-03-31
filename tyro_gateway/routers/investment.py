from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.stock_strategy import StockStrategy
from tyro_gateway.models.options_strategy import OptionsPlay
from tyro_gateway.models.real_estate import RealEstateEntry

router = APIRouter()

@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategy):
    return create_record("4.1", data.dict())

@router.post("/add-options-play")
def add_options_play(data: OptionsPlay):
    return create_record("4.2", data.dict())

@router.post("/add-real-estate")
def add_real_estate(data: RealEstateEntry):
    return create_record("4.3", data.dict())