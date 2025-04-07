# tyro_gateway/routers/resume_version.py

from fastapi import APIRouter, Request
from tyro_gateway.models.resume_version import ResumeVersion
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.2 Resume Versions - CREATE
@router.post("/add-resume-version")
def add_resume_version(data: ResumeVersion, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.2", data.dict())
    log_api_trigger(
        action_name="Add Resume Version",
        endpoint="/add-resume-version",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.2 Resume Versions - QUERY
@router.get("/resume-versions")
def list_resume_versions(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.2", page_size=limit)
    log_api_trigger(
        action_name="List Resume Versions",
        endpoint="/resume-versions",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res
