# models/resume_version.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ResumeVersion(BaseModel):
    title: str = Field(..., description="Notion 主欄位，建議等同 target_job_title")
    date_created: date = Field(..., description="建立日期")
    target_job_title: str = Field(..., description="履歷目標職位")
    resume_summary: str = Field(..., description="摘要簡介內容")
    cover_letter_content: str = Field(default="", description="Cover Letter 的內文")
    linked_application: Optional[str] = Field(default=None, description="關聯的應徵紀錄 UUID 或名稱")
