from pydantic import BaseModel
from typing import Optional
from datetime import date

class PersonalTax(BaseModel):
    total_tax: float
    agi: float
    tax_platform: str
    year: str
    filing_date: date
    withholding_paid: float
    refund_due: float
    notes: Optional[str] = ""
