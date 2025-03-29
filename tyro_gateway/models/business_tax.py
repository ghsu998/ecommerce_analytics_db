#models/business_tax.py

from pydantic import BaseModel
from datetime import date

class BusinessTaxInput(BaseModel):
    entity_type: str
    cogs: float
    business_name: str
    tax_year: int
    franchise_tax: float
    notes: str
    total_revenue: float
    estimated_tax_paid: float
    filing_date: date
