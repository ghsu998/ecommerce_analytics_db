from pydantic import BaseModel
from datetime import datetime

class APITrigger(BaseModel):
    action_name: str
    endpoint: str
    data_summary: str
    trigger_source: str
    timestamp: datetime  # ⬅️ 確保是 datetime，不是 date
    status: str
