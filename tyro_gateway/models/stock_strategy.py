from pydantic import BaseModel
from typing import Optional
from datetime import date

class StockStrategy(BaseModel):
    ticker: str
    position_size: float
    strategy_note: str
    action: str
    strike_price: float
    date: date
