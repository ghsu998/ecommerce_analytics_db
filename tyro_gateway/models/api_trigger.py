from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TriggerStatus(str, Enum):
    success = "Success"
    failed = "Failed"
    pending = "Pending"

class APITrigger(BaseModel):
    title: str  # Notion 要求有 Title 欄位作為主鍵
    user_identity: str  # <--- 加上這個
    action_name: str
    endpoint: str
    data_summary: str
    trigger_source: str
    timestamp: datetime  # ✅ 確保是 datetime
    status: TriggerStatus  # ✅ 對應 Notion Select 的格式
