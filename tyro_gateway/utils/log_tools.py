# tyro_gateway/utils/log_tools.py

from datetime import datetime
from tyro_gateway.utils.notion_client import create_record
from tyro_gateway.env_loader import get_gpt_mode

def log_trigger(code: str, action: str, endpoint: str, data: dict = None, status: str = "Success"):
    try:
        summary = data if data else {}
        record = {
            "title": action,
            "action_name": action,
            "endpoint": endpoint,
            "data_summary": str(summary),
            "trigger_source": "GPT",
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "user_identity": get_gpt_mode()
        }
        # 寫入 Trigger Log（5.1 是固定代碼）
        create_record("5.1", record)
    except Exception as e:
        print(f"⚠️ Trigger log failed: {e}")
