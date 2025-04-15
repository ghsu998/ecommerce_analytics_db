from fastapi import APIRouter, Request
from typing import Literal, List, Optional
from pydantic import BaseModel

# 🚀 引入對應的資料模型
from tyro_gateway.models.email_identity import EmailIdentity

# 📝 自訂的 log 工具（記錄 API 操作）
from tyro_gateway.utils.log_tools import log_api_trigger

# 🔐 產生唯一識別碼用（避免重複寫入）
from tyro_gateway.utils.unique_key_generator import generate_unique_key

# 🧠 Notion 操作核心函數
from tyro_gateway.utils.notion_client import (
    create_record_if_not_exists,
    query_records
)

# 📦 將 Notion 原始資料解析為 Pydantic Model
from tyro_gateway.utils.notion_parser import parse_notion_record

# 初始化 API router
router = APIRouter()

# ✅ 請求資料格式定義（限制只能 "create" 或 "query"）
class EmailIdentityActionRequest(BaseModel):
    action: Literal["create", "query"]
    data: EmailIdentity  # 內層資料直接對應到 model

# ✅ 回傳格式定義
class EmailIdentityResponse(BaseModel):
    status: str  # "success" 或 "error"
    message: Optional[str] = None
    record: Optional[EmailIdentity] = None
    results: Optional[List[EmailIdentity]] = None
    notion_id: Optional[str] = None

# ✅ 核心 API Endpoint
@router.post(
    "/email-identity",
    tags=["Email Identity"],
    summary="Create or query an email identity profile",
    response_model=EmailIdentityResponse
)
def handle_email_identity(
    request: Request,
    payload: EmailIdentityActionRequest
):
    # 取得使用者身份（可追蹤來源 GPT / chat / plugin）
    user_identity = request.headers.get("x-user-identity", "chat")

    # 取出動作類型與實際資料
    action = payload.action
    data = payload.data.dict()

    # ✅ 寫入觸發紀錄（log entry）
    log_api_trigger(
        action_name=f"EmailIdentity::{action}",
        endpoint="/email-identity",
        data_summary=data,
        trigger_source="GPT",
        user_identity=user_identity
    )

    # ✅ 建立資料邏輯
    if action == "create":
        # 如果沒提供 unique_key，就自動產生一組
        if not data.get("unique_key"):
            data["unique_key"] = generate_unique_key("email_identity", data)

        # 寫入 Notion，若重複會避免插入
        result = create_record_if_not_exists("2.1", data)

        # 把 Notion 回傳的資料轉成對應的 Pydantic model
        notion_data = result.get("record")
        record = parse_notion_record(notion_data, EmailIdentity) if notion_data else None

        # ✅ 回傳統一格式
        return EmailIdentityResponse(
            status=result.get("status"),
            message=result.get("message"),
            record=record,
            notion_id=result.get("notion_id")
        )

    # ✅ 查詢資料邏輯
    elif action == "query":
        try:
            raw_limit = data.get("limit", 10)
            limit = max(1, min(int(raw_limit), 100))  # 限定 1 ~ 100 範圍
        except (ValueError, TypeError):
            limit = 10  # fallback 預設值

        # 查詢 Notion Database（可自訂 page_size）
        status_code, response = query_records("2.1", page_size=limit)
        notion_results = response.get("results", [])

        # 把 Notion 結果一一轉換成 model
        parsed_results = [
            parse_notion_record(n, EmailIdentity) for n in notion_results
        ]

        return EmailIdentityResponse(
            status="success" if status_code == 200 else "error",
            results=parsed_results
        )

    # ❌ 若 action 不合法，回傳錯誤訊息
    return EmailIdentityResponse(
        status="error",
        message=f"❌ Unknown action '{action}' for Email Identity"
    )
