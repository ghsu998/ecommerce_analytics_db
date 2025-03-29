#models/stock_strategy.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class StockStrategyInput(BaseModel):
    ticker: str
    position_size: Optional[float] = 0
    strategy_note: Optional[str] = ""
    action: Optional[str] = ""
    strike_price: Optional[float] = 0
    date: date
