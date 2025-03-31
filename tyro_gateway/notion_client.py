
import json
import requests
from datetime import date, datetime
from typing import Optional

# 讀取 Notion token
with open("app_config.json", "r") as f:
    config = json.load(f)
NOTION_TOKEN = config["notion_token"]

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ✅ 所有 Notion DB ID 對照表
DB_MAP = {
    "1.1": {"name": "SO.Email Identity DB", "id": "1c42a656-d251-80c1-a3d9-d6ed033a60e5"},
    "1.2": {"name": "SO.Client CRM DB", "id": "1c42a656-d251-80c5-b261-f488a8c1ed04"},
    "2.1": {"name": "PS.Job Applications DB", "id": "1c32a656-d251-8037-915d-c0e9a52ef4d3"},
    "2.2": {"name": "PS.Resume Versions DB", "id": "1c32a656-d251-8047-be41-debb5c2e6c0d"},
    "3.1": {"name": "FD.Personal Tax DB", "id": "1c42a656-d251-80b1-b969-ebbf790ab828"},
    "3.2": {"name": "FD.Business Tax DB", "id": "1c42a656-d251-803b-b514-e843e5039cdd"},
    "4.1": {"name": "AG.Stock Strategy DB", "id": "1c42a656-d251-806f-9937-ddf04500ea15"},
    "4.2": {"name": "AG.Options Strategy DB", "id": "1c42a656-d251-80d6-9423-d36c3c55d606"},
    "4.3": {"name": "AG.Real Estate DB", "id": "1c42a656-d251-80e5-b765-caa4c5bc6b14"},
    "5.1": {"name": "EE.API Trigger Log", "id": "1c72a656-d251-8070-9f94-c8c44d0c5b3d"},
    "6.1": {"name": "DB.Strategy Master DB", "id": "1c72a656-d251-8073-af8f-e7a2c7fd0c14"},
}

# 🧠 將 Python 資料自動轉為 Notion 欄位格式
def to_notion_property(value):
    if isinstance(value, (str, int, float)):
        return {"rich_text": [{"text": {"content": str(value)}}]}
    elif isinstance(value, (date, datetime)):
        return {"date": {"start": str(value)}}
    elif isinstance(value, bool):
        return {"checkbox": value}
    elif value is None:
        return {"rich_text": [{"text": {"content": ""}}]}
    else:
        return {"rich_text": [{"text": {"content": str(value)}}]}

# ✅ 建立紀錄
def create_record(code: str, data: dict):
    db_id = DB_MAP[code]["id"]
    props = {}
    for k, v in data.items():
        if k.lower() == "title":
            props["Title"] = {"title": [{"text": {"content": str(v)}}]}
        else:
            props[k.replace("_", " ").title()] = to_notion_property(v)

    payload = {
        "parent": {"database_id": db_id},
        "properties": props
    }
    url = "https://api.notion.com/v1/pages"
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

# 🔍 查詢紀錄
def query_records(code: str, filter_conditions: Optional[dict] = None, page_size: int = 10):
    db_id = DB_MAP[code]["id"]
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": page_size}
    if filter_conditions:
        payload["filter"] = filter_conditions
    res = requests.post(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()

# ✏️ 更新紀錄
def update_record(page_id: str, updated_fields: dict):
    props = {}
    for k, v in updated_fields.items():
        if k.lower() == "title":
            props["Title"] = {"title": [{"text": {"content": str(v)}}]}
        else:
            props[k.replace("_", " ").title()] = to_notion_property(v)

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": props}
    res = requests.patch(url, headers=HEADERS, json=payload)
    return res.status_code, res.json()
