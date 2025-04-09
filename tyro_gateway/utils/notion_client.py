# tyro_gateway/utils/notion_client.py

import os
import json
import requests
from datetime import datetime, date
from typing import Optional
from tyro_gateway.env_loader import get_gpt_mode
from tyro_gateway.models.api_trigger import APITrigger

# ✅ 載入 Notion Token 與 GPT 模式
with open("app_config.json", "r") as f:
    config = json.load(f)
NOTION_TOKEN = config["notion_token"]
GPT_MODE = get_gpt_mode()

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ✅ 所有 Notion DB ID 對照表
DB_MAP = {
    "1.1": {"name": "API Trigger Log", "id": "1c72a656-d251-8070-9f94-c8c44d0c5b3d"},
    "2.1": {"name": "Email Identity DB", "id": "1c42a656-d251-80c1-a3d9-d6ed033a60e5"},
    "2.2": {"name": "Job Applications DB", "id": "1c32a656-d251-8037-915d-c0e9a52ef4d3"},
    "2.3": {"name": "Resume Versions DB", "id": "1c32a656-d251-8047-be41-debb5c2e6c0d"},
    "2.4": {"name": "Personal Tax DB", "id": "1c42a656-d251-80b1-b969-ebbf790ab828"},
    "2.5": {"name": "Business Tax DB", "id": "1c42a656-d251-803b-b514-e843e5039cdd"},
    "2.6": {"name": "Stock Strategy DB", "id": "1c42a656-d251-806f-9937-ddf04500ea15"},
    "2.7": {"name": "Options Strategy DB", "id": "1c42a656-d251-80d6-9423-d36c3c55d606"},
    "2.8": {"name": "Real Estate DB", "id": "1c42a656-d251-80e5-b765-caa4c5bc6b14"},
    "2.9": {"name": "Strategy Master DB", "id": "1c72a656-d251-8073-af8f-e7a2c7fd0c14"},
    "3.1": {"name": "Client CRM DB", "id": "1c42a656-d251-80c5-b261-f488a8c1ed04"}
}

# ✅ 特殊欄位對應（避免大小寫錯誤）
FIELD_MAP = {
    "2.5": {
        "entity_type": "Entity Type",
        "tax_year": "Tax Year",
        "total_revenue": "Total Revenue",
        "cogs": "COGS",
        "total_expenses": "Total Expenses",
        "net_income": "Net Income",
        "franchise_tax": "Franchise Tax",
        "estimated_tax_paid": "Estimated Tax Paid",
        "filing_date": "Filing Date",
        "business_name": "Business Name",
        "notes": "Notes",
    },
    "2.9": {
        "module_project": "Module Project"
    }
}

# ✅ 型別轉換：Python → Notion
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

# ✅ 建立紀錄 + 自動記錄觸發紀錄
def create_record(code: str, data: dict):
    db_id = DB_MAP[code]["id"]
    db_name = DB_MAP[code]["name"]
    field_map = FIELD_MAP.get(code, {})

    props = {}

    for k, v in data.items():
        if k.lower() == "title" and v:
            props["title"] = {
                "title": [{"text": {"content": str(v)}}]
            }
        else:
            notion_key = field_map.get(k, k.replace("_", " ").title())
            props[notion_key] = to_notion_property(v)

    payload = {
        "parent": {"database_id": db_id},
        "properties": props
    }

    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)

    # ✅ 加入錯誤檢查與 debug 輸出
    if res.status_code != 200:
        print(f"❌ Notion create_record failed: {res.status_code}")
        print("→ Response:", res.text)
        return {"status": "error", "reason": res.text}

    # ✅ 自動記錄 API Trigger Log（避免遞迴自己）
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

# ✅ 查詢 Notion 資料
def query_records(code: str, filter_conditions: Optional[dict] = None, page_size: int = 10):
    db = DB_MAP.get(code)
    if not db:
        raise ValueError(f"❌ DB code '{code}' not found in DB_MAP.")
    db_id = db["id"]
    db_name = db["name"]

    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": page_size}
    if filter_conditions:
        payload["filter"] = filter_conditions
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()
