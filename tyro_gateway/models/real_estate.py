from pydantic import BaseRealEstate
from typing import Optional
from datetime import date

class RealEstate(BaseRealEstate):
    monthly_insurance: float
    purchase_date: date
    purchase_price: float
    property_address: str
    monthly_cash_flow: float
    monthly_property_taxes: float
    monthly_mortgage_payment: float
    monthly_utility_expenses: float
    notes: Optional[str]
    loan_amount: float
    strategy: Optional[str]
