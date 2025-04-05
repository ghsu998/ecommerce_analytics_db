import sys, os

# ✅ 加入專案根目錄到 sys.path（支援 VSCode ▶️、CLI、VPS 運行）
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from app_config import logger
from tyro_data_clean.utils import client_file_mapping_config
from tyro_data_clean.utils import client_file_xlsx_convert_google_sheet
from tyro_data_clean.apis.api_google import get_google_drive_service
from tyro_data_clean.apis.api_microsoft import authenticate_microsoft
from tyro_data_clean.tasks import client_process_raw_data

def main():
    # 🔁 取得所有客戶
    clients = client_file_mapping_config.get_clients_list()
    if not clients:
        logger.error("❌ 無任何可處理的客戶，請確認 `clients_file_mapping_table` 有資料")
        return

    logger.info(f"🚀 開始處理 {len(clients)} 個客戶...")

    # ✅ 初始化兩個雲端服務
    google_service = get_google_drive_service()
    microsoft_token = authenticate_microsoft()

    for client_id in clients:
        logger.info(f"\n🔁 處理中: {client_id}")
        client_config = client_file_mapping_config.get_client_data_settings(client_id)
        if not client_config:
            logger.warning(f"⚠️ 找不到 `{client_id}` 配置，跳過")
            continue

        storage_type = client_config.get("storage_type", "google_drive")
        service = google_service if storage_type == "google_drive" else microsoft_token

        # ✅ 清理原始資料、產出 master.xlsx
        client_process_raw_data.process_client_raw_data(
            client_id=client_id,
            storage_type=storage_type,
            service=service,
            user_email=None
        )

        # ✅ 若是 Google Drive，再轉為 Google Sheets
        if storage_type == "google_drive":
            client_file_xlsx_convert_google_sheet.convert_single_client_master_xlsx(client_id)

    logger.info("🎯 所有客戶處理完成！")

if __name__ == "__main__":
    main()
