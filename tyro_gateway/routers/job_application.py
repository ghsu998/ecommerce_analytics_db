from fastapi import APIRouter, Request
from tyro_gateway.models.job_application import JobApplication
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.utils.log_tools import log_api_trigger

router = APIRouter()

# 📌 2.2 Job Applications - CREATE
@router.post("/add-job-application")
def add_job_application(data: JobApplication, request: Request):
    user_identity = request.headers.get("x-user-identity", "chat")
    res = create_record("2.2", data.dict())
    log_api_trigger(
        action_name="Add Job Application",
        endpoint="/add-job-application",
        data_summary=data.dict(),
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res

# 📌 2.2 Job Applications - QUERY
@router.get("/job-applications")
def list_job_applications(limit: int = 10, request: Request = None):
    user_identity = request.headers.get("x-user-identity", "chat") if request else "chat"
    res = query_records("2.2", page_size=limit)
    log_api_trigger(
        action_name="List Job Applications",
        endpoint="/job-applications",
        data_summary={"limit": limit},
        trigger_source="GPT",
        user_identity=user_identity
    )
    return res
