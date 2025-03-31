from pydantic import BaseStrategy
from typing import Optional
from datetime import date

class Strategy(BaseStrategy):
    notes: Optional[str]
    category: str
    objective: str
    module_project: str
    phase: str
    strategy_name: str
