# 📁 tyro_gateway/routers/investment.py
from fastapi import APIRouter
from tyro_gateway.models.stock_strategy import StockStrategyInput
from tyro_gateway.models.options_play import OptionsPlayInput
from tyro_gateway.models.real_estate import RealEstateInput
from tyro_gateway.notion_client import (
    create_stock_strategy,
    create_options_play,
    create_real_estate_entry,
)

router = APIRouter()

# 3.1 Stock Strategy Log
@router.post("/add-stock-strategy")
def add_stock_strategy(data: StockStrategyInput):
    status, response = create_stock_strategy(data)
    return {"status": status, "response": response}

# 3.2 Options Play Log
@router.post("/add-options-play")
def add_options_play(data: OptionsPlayInput):
    status, response = create_options_play(data)
    return {"status": status, "response": response}

# 3.3 Real Estate Tracker
@router.post("/add-real-estate")
def add_real_estate_entry(data: RealEstateInput):
    status, response = create_real_estate_entry(data)
    return {"status": status, "response": response}
