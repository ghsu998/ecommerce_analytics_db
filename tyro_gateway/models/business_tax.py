#models/business_tax.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class BusinessTaxInput(BaseModel):
    business_name: str
    entity_type: str
    tax_year: int
    total_revenue: float
    cogs: float
    franchise_tax: float
    estimated_tax_paid: float
    filing_date: str  # "YYYY-MM-DD"
    notes: Optional[str] = None

    # 新增欄位
    net_income: Optional[float] = None
    total_expenses: Optional[float] = None

