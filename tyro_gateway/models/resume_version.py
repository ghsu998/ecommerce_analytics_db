from pydantic import BaseResumeVersion
from typing import Optional
from datetime import date

class ResumeVersion(BaseResumeVersion):
    resume_summary: str
    target_job_title: str
    date_created: date
    cover_letter_content: Optional[str]
    linked_application: Optional[str]
