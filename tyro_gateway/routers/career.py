from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.job_application import JobApplication
from tyro_gateway.models.resume_version import ResumeVersion

router = APIRouter()

@router.post("/add-job-application")
def add_job_application(data: JobApplication):
    return create_record("2.1", data.dict())

@router.post("/add-resume-version")
def add_resume_version(data: ResumeVersion):
    return create_record("2.2", data.dict())