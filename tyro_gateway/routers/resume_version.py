# ✅ tyro_gateway/routers/resume_version.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

from tyro_gateway.models.resume_version import ResumeVersion
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)
from tyro_gateway.utils.notion_parser import parse_notion_record

router = APIRouter()

class ResumeVersionActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: ResumeVersion

class ResumeVersionResponse(BaseModel):
    status: str
    message: Optional[str] = None
    record: Optional[ResumeVersion] = None
    results: Optional[List[ResumeVersion]] = None
    notion_id: Optional[str] = None

@router.post(
    "/resume-version",
    tags=["Resume Version"],
    summary="Create or query a resume version record",
    response_model=ResumeVersionResponse
)
def handle_resume_version(
    request: Request,
    payload: ResumeVersionActionRequest
):
    user_identity = request.headers.get("x-user-identity", "chat")
    action = payload.action
    data = payload.data.dict()

    log_api_trigger(
        action_name=f"ResumeVersion::{action}",
        endpoint="/resume-version",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    if action == "create":
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("resume_version", data)
        result = create_record_if_not_exists("2.3", data)
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, ResumeVersion) if notion_data else None
        return ResumeVersionResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    elif action == "query":
        limit = data.get("limit", 10)
        status_code, response = query_records("2.3", page_size=limit)
        notion_results = response.get("results", [])
        parsed_results = [
            parse_notion_record(n, ResumeVersion) for n in notion_results
        ]
        return ResumeVersionResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    return ResumeVersionResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Resume Version"
    )
