# ✅ tyro_gateway/routers/resume_version.py（重構為 GPT Plugin 標準格式）

from fastapi import APIRouter, Request
from typing import Dict, Any, Literal
from pydantic import BaseModel

from tyro_gateway.models.resume_version import ResumeVersion
from tyro_gateway.utils.log_tools import log_api_trigger
from tyro_gateway.utils.unique_key_generator import generate_unique_key
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

router = APIRouter()

class ResumeVersionActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: ResumeVersion

@router.post(
    "/resume-version",
    tags=["Resume Version"],
    summary="Create or query a resume version record",
    response_model=Dict[str, Any]
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
        return create_record_if_not_exists("2.3", data)

    elif action == "query":
        limit = data.get("limit", 10)
        return query_records("2.3", page_size=limit)

    return {
        "status": "error",
        "message": f"❌ Unknown action '{action}' for Resume Version"
    }
