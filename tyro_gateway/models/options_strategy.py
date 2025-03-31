from pydantic import BaseModel
from typing import Optional
from datetime import date

class OptionsStrategy(BaseModel):
    delta: Optional[float] = None
    ticker: str
    option_strategy: str
    created_date: date
    expiration: Optional[date] = None
    action: Optional[str] = ""
    entry_option_price: Optional[float] = 0
    contract_size: Optional[int] = 1
    strategy_note: Optional[str] = ""
