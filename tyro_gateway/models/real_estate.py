# models/real_estate.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class RealEstateInput(BaseModel):
    purchase_date: date
    purchase_price: float
    property_address: str
    monthly_cash_flow: Optional[float] = 0.0
    notes: Optional[str] = ""
    loan_amount: Optional[float] = 0.0
    strategy: Optional[str] = ""
