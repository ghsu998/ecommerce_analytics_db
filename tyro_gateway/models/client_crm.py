# models/client_crm.py

from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import date
from enum import Enum

class ClientStatus(str, Enum):
    lead = "Lead"
    active = "Active"
    lost = "Lost"

class ClientCRM(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，對應 Client Name")
    client_company: str = Field(..., description="客戶所屬公司名稱")
    client_name: str = Field(..., description="客戶名稱")
    client_email: EmailStr = Field(..., description="客戶電子郵件")
    client_phone: str = Field(..., description="客戶電話")
    client_address: str = Field(..., description="客戶地址")
    status: str = Field(..., description="目前狀態（Lead, Active, Lost）")
    client_last_contacted: date = Field(..., description="最近聯繫日期")
    assigned_to_identity: str = Field(..., description="分配給哪個 GPT 身分")
    client_notes: str = Field(default="", description="其他備註")
    unique_key: str = Field(..., description="唯一識別碼，建議使用 client_name + client_company + client_email")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            values["title"] = values.get("client_name", "")
        return values

