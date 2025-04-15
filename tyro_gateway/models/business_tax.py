# models/business_tax.py

from pydantic import BaseModel, Field, model_validator
from datetime import date

class BusinessTax(BaseModel):
    title: str = Field(..., description="供 Notion Title 使用，對應 business_name")
    filing_date: date
    business_name: str
    entity_type: str
    tax_year: int
    total_revenue: int
    cogs: int = Field(..., alias="Cogs")  # ✅ Notion 欄位別名
    total_expenses: int
    net_income: int
    franchise_tax: int
    estimated_tax_paid: int
    notes: str = ""
    unique_key: str = Field(..., description="供 Notion Unique Key 使用，建議對應 business_name + tax_year")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            values["title"] = values.get("business_name", "")
        return values


