from pydantic import BaseModel
from typing import Optional
from datetime import date
from datetime import datetime

class APITrigger(BaseModel):
    timestamp: datetime
    trigger_source: str
    status: str
    data_summary: str
    endpoint: str
    action_name: str
