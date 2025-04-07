from app_config import logger
from tyro_data_db.schema_models import insert_datacenter_mapping_record

def insert_or_ignore_datacenter_mapping(client_id: str, tab: str, col: str):
    """
    🧩 將欄位加入 `client_datacenter_mapping_table`
    - 若已存在（client_id, tab, col）則忽略
    """
    try:
        success = insert_datacenter_mapping_record(
            client_id=client_id,
            datacenter_tab=tab,
            client_column=col,
            is_required=False  # ✅ 預設為 False，留給用戶後續 UI 設定
        )

        if success:
            logger.info(f"✅ [Mapping] 已新增欄位 `{col}` 至 `{tab}` for `{client_id}`")
        else:
            logger.info(f"⏩ [Mapping] `{col}` 已存在於 `{tab}` for `{client_id}`，略過")

    except Exception as e:
        logger.error(f"❌ 無法新增 Mapping: {e}")
