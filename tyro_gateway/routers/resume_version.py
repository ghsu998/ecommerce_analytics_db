# tyro_gateway/routers/career.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.resume_version import ResumeVersion

router = APIRouter()



# 2.2 Resume Version - CREATE
@router.post("/add-resume-version")
def add_resume_version(data: ResumeVersion):
    return create_record("2.2", data.dict())



# 2.2 Resume Version - QUERY
@router.get("/resume-versions")
def list_resume_versions(limit: int = 10):
    return query_records("2.2", page_size=limit)
