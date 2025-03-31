from pydantic import BasePersonalTax
from typing import Optional
from datetime import date

class PersonalTax(BasePersonalTax):
    total_tax: float
    agi: float
    tax_platform: str
    year: str
    filing_date: date
    withholding_paid: float
    refund_due: float
    notes: Optional[str]
