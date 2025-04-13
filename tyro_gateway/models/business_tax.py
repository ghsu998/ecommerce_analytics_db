from pydantic import BaseModel
from datetime import date

class BusinessTax(BaseModel):
    title: str  # ✅ 供 Notion Title 使用，對應 Business Name
    filing_date: date
    business_name: str
    entity_type: str
    tax_year: int
    total_revenue: int
    cogs: int
    total_expenses: int
    net_income: int
    franchise_tax: int
    estimated_tax_paid: int
    notes: str = ""
    unique_key: str  # ✅ 供 Notion Unique Key 使用，建議對應 business_name + tax_year
