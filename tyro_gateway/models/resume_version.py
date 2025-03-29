# models/resume_version.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

class ResumeVersionInput(BaseModel):
    resume_summary: str
    target_job_title: str
    date_created: date
    cover_letter_content: Optional[str] = ""
