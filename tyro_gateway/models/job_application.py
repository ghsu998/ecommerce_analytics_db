# models/job_application.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

class JobApplicationInput(BaseModel):
    date_applied: date
    job_title: str
    company_name: str
    status: str
    job_type: str
    notes: Optional[str] = None
