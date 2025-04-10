# tyro_gateway/models/retailer_crm.py

from pydantic import BaseModel, Field, EmailStr
from datetime import date
from enum import Enum

class RetailerStatus(str, Enum):
    lead = "Lead"
    active = "Active"
    lost = "Lost"

class RetailerCRM(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，對應 Retailer 名稱")
    retailer_company: str = Field(..., description="零售商公司名稱")
    retailer_website: str = Field(default="", description="公司官網網址")
    retailer_department: str = Field(..., description="零售商公司產品類別")
    contact_name: str = Field(..., description="聯絡人名稱")
    contact_email: EmailStr = Field(..., description="聯絡人 Email")
    contact_phone: str = Field(..., description="聯絡人電話")
    status: RetailerStatus = Field(..., description="目前狀態（Lead, Active, Lost）")
    last_contacted: date = Field(..., description="最近聯繫日期")
    assigned_to_identity: str = Field(..., description="分配給哪個 GPT 身分")
    notes: str = Field(default="", description="備註")
