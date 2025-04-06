# models/client_crm.py

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class ClientStatus(str, Enum):
    lead = "Lead"
    active = "Active"
    lost = "Lost"

class ClientCRM(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，對應 Client Name")
    client_name: str = Field(..., description="客戶名稱")
    client_company: str = Field(..., description="客戶所屬公司名稱")
    status: ClientStatus = Field(..., description="目前狀態（Lead, Active, Lost）")
    client_last_contacted: date = Field(..., description="最近聯繫日期")
    assigned_to_identity: str = Field(..., description="分配給哪個 GPT 身分")
    client_notes: str = Field(default="", description="其他備註")
