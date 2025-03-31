from pydantic import BaseBusinessTax
from typing import Optional
from datetime import date

class BusinessTax(BaseBusinessTax):
    entity_type: str
    cogs: float
    business_name: str
    tax_year: int
    total_expenses: Optional[float]
    net_income: Optional[float]
    franchise_tax: float
    notes: Optional[str]
    total_revenue: float
    estimated_tax_paid: float
    filing_date: date
