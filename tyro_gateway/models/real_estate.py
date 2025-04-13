# models/real_estate.py

from pydantic import BaseModel, Field
from datetime import date

class RealEstate(BaseModel):
    title: str = Field(..., description="Notion 主欄位，建議用地址或策略自動產出")
    purchase_date: date = Field(..., description="購屋日期")
    strategy: str = Field(..., description="策略類型，例如 自住、自租、Airbnb 等")
    property_address: str = Field(..., description="物件地址")
    purchase_price: float = Field(..., description="購買總價")
    loan_amount: float = Field(..., description="貸款金額")
    monthly_cash_flow: float = Field(..., description="每月現金流")
    monthly_mortgage_payment: float = Field(..., description="每月房貸金額")
    monthly_property_taxes: float = Field(..., description="每月房屋稅")
    monthly_insurance: float = Field(..., description="每月保費")
    monthly_utility_expenses: float = Field(..., description="每月水電雜費")
    notes: str = Field(default="", description="備註")
    unique_key: str = Field(..., description="唯一識別碼，建議用 property_address 做為唯一標識")