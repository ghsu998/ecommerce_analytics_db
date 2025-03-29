#models/options_play.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

from pydantic import BaseModel
from datetime import date
from typing import Optional

class OptionsPlayInput(BaseModel):
    delta: Optional[float] = None
    ticker: str
    option_strategy: str
    date: date
    expiration: date # type: ignore
    action: Optional[str] = ""
    entry_option_price: Optional[float] = 0.0
    contract_size: Optional[int] = 1
    strategy_note: Optional[str] = ""
