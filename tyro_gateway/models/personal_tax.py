# models/personal_tax.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class PersonalTaxInput(BaseModel):
    total_tax: float
    agi: float
    tax_platform: str
    year: str
    filing_date: date
    withholding_paid: float
    refund_due: float
    notes: Optional[str] = ""
