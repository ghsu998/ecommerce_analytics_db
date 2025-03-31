from pydantic import BaseModel
from typing import Optional
from datetime import date

class JobApplication(BaseModel):
    date_applied: date
    job_type: str
    status: str
    resume_version: str
    company_name: str
    notes: Optional[str]
    job_title: str
