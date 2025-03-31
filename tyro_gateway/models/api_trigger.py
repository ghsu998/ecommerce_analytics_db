from pydantic import BaseModel
from typing import Optional
from datetime import date

class APITrigger(BaseModel):
    timestamp: date
    trigger_source: str
    status: str
    data_summary: str
    endpoint: str
    action_name: str
