# models/resume_version.py

from pydantic import BaseModel, Field, model_validator
from datetime import date

class ResumeVersion(BaseModel):
    title: str = Field(..., description="Notion 主欄位，建議等同 target_job_title")
    date_created: date = Field(..., description="建立日期")
    target_job_title: str = Field(..., description="履歷目標職位")
    resume_summary: str = Field(..., description="摘要簡介內容")
    cover_letter_content: str = Field(default="", description="Cover Letter 的內文")
    unique_key: str = Field(..., description="唯一識別碼，建議使用 target_job_title + date_created")

    @model_validator(mode="before")
    @classmethod
    def auto_title(cls, values):
        if not values.get("title"):
            values["title"] = values.get("target_job_title", "")
        return values