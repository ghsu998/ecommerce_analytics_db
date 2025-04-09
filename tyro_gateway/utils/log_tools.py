from tyro_gateway.models.api_trigger import APITrigger
from tyro_gateway.utils.notion_client import create_record
from datetime import datetime

def log_api_trigger(action_name: str, endpoint: str, data_summary: dict, trigger_source: str, user_identity: str = "GPT", status: str = "✅ Success"):
    return create_record("1.1", APITrigger(
        title=action_name,
        action_name=action_name,
        endpoint=endpoint,
        data_summary=str(data_summary),
        trigger_source=trigger_source,
        user_identity=user_identity,
        timestamp=datetime.utcnow(),
        status=status.replace("✅", "").strip() if status else "Success",

    ).dict())
