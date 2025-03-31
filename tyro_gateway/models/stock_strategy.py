from pydantic import BaseStockStrategy
from typing import Optional
from datetime import date

class StockStrategy(BaseStockStrategy):
    ticker: str
    position_size: Optional[float]
    strategy_note: Optional[str]
    action: Optional[str]
    strike_price: Optional[float]
    date: date
