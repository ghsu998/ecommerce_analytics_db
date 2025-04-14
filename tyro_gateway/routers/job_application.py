# ✅ tyro_gateway/routers/job_application.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.job_application import JobApplication
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

# ✅ Request schema
class JobApplicationActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: JobApplication

# ✅ Response schema (引用 model)
class JobApplicationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[JobApplication] = None
    results: Optional[List[JobApplication]] = None
    notion_id: Optional[str] = None

@router.post(
    "/job-application",
    tags=["Job Application"],
    summary="Create or query a job application record",
    response_model=JobApplicationResponse
)
def handle_job_application(
    request: Request,
    payload: JobApplicationActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"JobApplication::{action}",
        endpoint="/job-application",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("job_application", data)
        result = create_record_if_not_exists("2.2", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, JobApplication) if notion_data else None
        return JobApplicationResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    elif action == "query":
        limit = data.get("limit", 10)
        status_code, response = query_records("2.2", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, JobApplication) for n in notion_results
        ]
        return JobApplicationResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    return JobApplicationResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Job Application"
    )
