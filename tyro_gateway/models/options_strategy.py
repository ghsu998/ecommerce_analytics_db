from pydantic import BaseOptionsPlay
from typing import Optional
from datetime import date

class OptionsPlay(BaseOptionsPlay):
    delta: Optional[float]
    ticker: str
    option_strategy: str
    date: date
    expiration: date
    action: Optional[str]
    entry_option_price: Optional[float]
    contract_size: Optional[int]
    strategy_note: Optional[str]
