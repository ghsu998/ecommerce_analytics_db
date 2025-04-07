# tyro_gateway/routers/career.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.job_application import JobApplication

router = APIRouter()

# 2.1 Job Application - CREATE
@router.post("/add-job-application")
def add_job_application(data: JobApplication):
    return create_record("2.1", data.dict())



# 2.1 Job Application - QUERY
@router.get("/job-applications")
def list_job_applications(limit: int = 10):
    return query_records("2.1", page_size=limit)
