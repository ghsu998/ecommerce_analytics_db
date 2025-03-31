from pydantic import BaseModel
from typing import Optional
from datetime import date

class JobApplication(BaseModel):
    date_applied: date
    job_title: str
    company_name: str
    status: str
    job_type: str
    resume_version: Optional[str] = None
    notes: Optional[str] = ""
