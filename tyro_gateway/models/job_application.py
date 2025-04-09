# models/job_application.py

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class JobStatus(str, Enum):
    applied = "Applied"
    interview = "Interview"
    offer = "Offer"
    rejected = "Rejected"
    withdrawn = "Withdrawn"

class JobApplication(BaseModel):
    title: str = Field(..., description="Notion 主索引欄位，建議等同 job_title")
    date_applied: date = Field(..., description="送出申請的日期")
    status: JobStatus = Field(..., description="目前申請狀態")
    job_type: str = Field(..., description="Remote / Onsite / Hybrid")
    job_title: str = Field(..., description="應徵職缺名稱")
    company_name: str = Field(..., description="公司名稱")
    notes: str = Field(default="", description="其他備註，例如申請來源、特殊提醒")
