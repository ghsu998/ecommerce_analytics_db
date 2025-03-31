from pydantic import BaseModel
from typing import Optional
from datetime import date

class RealEstateEntry(BaseModel):
    purchase_date: date
    purchase_price: float
    loan_amount: float
    property_address: str
    strategy: Optional[str] = ""
    notes: Optional[str] = ""
    monthly_cash_flow: float
    monthly_mortgage_payment: float
    monthly_property_taxes: float
    monthly_insurance: float
    monthly_utility_expenses: float
