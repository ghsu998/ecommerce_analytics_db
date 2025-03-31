from fastapi import APIRouter
from tyro_gateway.notion_client import create_record, query_records
from tyro_gateway.models.job_application import JobApplication
from tyro_gateway.models.resume_version import ResumeVersion

router = APIRouter()

# 2.1 Job Application - CREATE
@router.post("/add-job-application")
def add_job_application(data: JobApplication):
    return create_record("2.1", data.dict())

# 2.2 Resume Version - CREATE
@router.post("/add-resume-version")
def add_resume_version(data: ResumeVersion):
    return create_record("2.2", data.dict())

# 2.1 Job Application - QUERY
@router.get("/job-applications")
def list_job_applications(limit: int = 10):
    return query_records("2.1", page_size=limit)

# 2.2 Resume Version - QUERY
@router.get("/resume-versions")
def list_resume_versions(limit: int = 10):
    return query_records("2.2", page_size=limit)
