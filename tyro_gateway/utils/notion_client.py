# tyro_gateway/utils/notion_client.py

import os
import json
import requests
from datetime import datetime, date
from typing import Optional
from tyro_gateway.env_loader import get_gpt_mode
from tyro_gateway.models.api_trigger import APITrigger

# ✅ 載入設定與身份
with open("app_config.json", "r") as f:
    config = json.load(f)

NOTION_TOKEN = config["notion_token"]
GPT_MODE = get_gpt_mode()

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ✅ 所有 Notion Database 對照表（代碼 → 名稱 + DB ID）
DB_MAP = {
    "1.1": {"name": "API Trigger Log",         "id": "1c72a656-d251-8070-9f94-c8c44d0c5b3d"},
    "2.1": {"name": "Email Identity DB",       "id": "1c42a656-d251-80c1-a3d9-d6ed033a60e5"},
    "2.2": {"name": "Job Applications DB",     "id": "1c32a656-d251-8037-915d-c0e9a52ef4d3"},
    "2.3": {"name": "Resume Versions DB",      "id": "1c32a656-d251-8047-be41-debb5c2e6c0d"},
    "2.4": {"name": "Personal Tax DB",         "id": "1c42a656-d251-80b1-b969-ebbf790ab828"},
    "2.5": {"name": "Business Tax DB",         "id": "1c42a656-d251-803b-b514-e843e5039cdd"},
    "2.6": {"name": "Stock Strategy DB",       "id": "1c42a656-d251-806f-9937-ddf04500ea15"},
    "2.7": {"name": "Options Strategy DB",     "id": "1c42a656-d251-80d6-9423-d36c3c55d606"},
    "2.8": {"name": "Real Estate DB",          "id": "1c42a656-d251-80e5-b765-caa4c5bc6b14"},
    "2.9": {"name": "Strategy Master DB",      "id": "1c72a656-d251-8073-af8f-e7a2c7fd0c14"},
    "3.1": {"name": "Client CRM DB",           "id": "1c42a656-d251-80c5-b261-f488a8c1ed04"},
    "3.2": {"name": "Retailer CRM DB",         "id": "1d12a656-d251-808b-92b2-db7f17a6966d"}
}

# ✅ 將 Python 資料轉換成 Notion Property 格式
def to_notion_property(value):
    if isinstance(value, (int, float)):
        return {"number": value}
    elif isinstance(value, str):
        return {"rich_text": [{"text": {"content": value}}]}
    elif isinstance(value, (date, datetime)):
        return {"date": {"start": str(value)}}
    elif isinstance(value, bool):
        return {"checkbox": value}
    elif value is None:
        return {"rich_text": [{"text": {"content": ""}}]}
    else:
        return {"rich_text": [{"text": {"content": str(value)}}]}

# ✅ 建立 Notion 紀錄，並觸發 log（自動寫入 1.1）
def create_record(code: str, data: dict):
    db_id = DB_MAP[code]["id"]
    db_name = DB_MAP[code]["name"]

    props = {}
    for k, v in data.items():
        if k.lower() == "title" and v:
            props["title"] = {"title": [{"text": {"content": str(v)}}]}
        else:
            # 目前 FIELD_MAP 廢用，直接 fallback 用轉換邏輯
            notion_key = k.replace("_", " ").title()
            props[notion_key] = to_notion_property(v)

    payload = {
        "parent": {"database_id": db_id},
        "properties": props
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)

    if res.status_code != 200:
        print(f"❌ Notion create_record failed: {res.status_code}")
        print("→ Response:", res.text)
        return {"status": "error", "reason": res.text}

    # ✅ 自動記錄 API 呼叫紀錄（避免自己再觸發自己）
    if code != "1.1":
        try:
            summary_fields = ["title", "strategy_date", "action", "ticker"]
            data_summary = {k: v for k, v in data.items() if k in summary_fields}

            trigger_data = APITrigger(
                title=f"Create Record: {code}",
                action_name=f"create_record_{code}",
                endpoint=f"/notion/create/{code}",
                data_summary=json.dumps(data_summary, ensure_ascii=False),
                trigger_source="GPT",
                timestamp=datetime.utcnow().isoformat(),
                status="Success",
                user_identity=GPT_MODE
            )
            create_record("1.1", trigger_data.dict())
        except Exception as e:
            print(f"⚠️ Failed to log API trigger to '1.1': {e}")

    return {"status": "success", "notion_id": res.json().get("id")}

# ✅ 查詢 Notion 紀錄
def query_records(code: str, filter_conditions: Optional[dict] = None, page_size: int = 10):
    db = DB_MAP.get(code)
    if not db:
        raise ValueError(f"❌ DB code '{code}' not found in DB_MAP.")
    db_id = db["id"]

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": page_size}
    if filter_conditions:
        payload["filter"] = filter_conditions

    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

# ✅ 若 unique_key 已存在，則不建立，直接回傳現有資料
def create_record_if_not_exists(code: str, data: dict, unique_key_field: str = "unique_key"):
    from .notion_client import create_record, query_records

    unique_key = data.get(unique_key_field)
    if not unique_key:
        raise ValueError("❌ 無法建立資料：缺少 unique_key")

    # 組 filter 查詢 Notion DB 是否已有相同 unique_key
    filter_conditions = {
        "property": unique_key_field.replace("_", " ").title(),
        "rich_text": {
            "equals": unique_key
        }
    }
    status_code, response = query_records(code, filter_conditions=filter_conditions, page_size=1)

    if status_code == 200 and response.get("results"):
        return {
            "status": "skipped",
            "message": f"⚠️ 資料已存在（unique_key: {unique_key}）",
            "record": response["results"][0]
        }

    return create_record(code, data)
