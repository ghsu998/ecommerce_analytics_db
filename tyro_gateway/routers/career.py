# 📁 tyro_gateway/routers/career.py
from fastapi import APIRouter
from tyro_gateway.models.job_application import JobApplicationInput
from tyro_gateway.models.resume_version import ResumeVersionInput
from tyro_gateway.notion_client import create_job_application, create_resume_version

router = APIRouter()

# 1.1 Job Application Tracker
@router.post("/add-job-application")
def add_job_application(data: JobApplicationInput):
    status, response = create_job_application(data)
    return {"status": status, "response": response}

# 1.2 Resume + Cover Letter Version Tracker
@router.post("/add-resume-version")
def add_resume_version(data: ResumeVersionInput):
    status, response = create_resume_version(data)
    return {"status": status, "response": response}
