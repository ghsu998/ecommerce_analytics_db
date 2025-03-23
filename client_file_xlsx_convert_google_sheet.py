from app_config import get_config_value, logger
from api_google_drive_functions import (
    convert_xlsx_to_google_sheet, get_google_drive_service, 
    list_gdrive_files, get_gdrive_folder_id
)
from client_file_mapping_config import get_clients_list, get_client_data_settings

def convert_all_clients_master_xlsx():
    """
    🔄 **針對所有客戶，搜尋 `_master.xlsx` 檔案並轉換為 Google Sheets**
    ✅ 確保：
       - `_master.xlsx` 只轉換對應 `client_data_folder` 的 Google Sheets
       - 已存在的 Google Sheets **被覆蓋，而不是新建**
       - `IMPORTRANGE()` 不會因為 Google Sheets ID 變動而失效
    """
    service = get_google_drive_service()  # 取得 Google Drive API 服務對象
    if not service:
        logger.error("❌ Google Drive API 服務無法連接")
        return

    clients = get_clients_list()  # 取得所有客戶清單
    if not clients:
        logger.warning("⚠️ 沒有找到任何客戶，請確認 `clients_file_mapping_table` 是否正確")
        return

    logger.info(f"🔍 開始處理 {len(clients)} 個客戶的 `_master.xlsx` 檔案...")

    # 📂 Google Drive 根目錄 ID
    root_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])

    for client_id in clients:
        client_info = get_client_data_settings(client_id)
        if not client_info:
            logger.warning(f"⚠️ 客戶 `{client_id}` 設置錯誤，跳過...")
            continue

        client_folder_name = client_info["client_data_folder"]
        storage_type = client_info["storage_type"]

        # ✅ **確保只處理 Google Drive**
        if storage_type.lower() != "google_drive":
            logger.warning(f"⚠️ `{client_id}` 使用的是 `{storage_type}`，跳過 Google Drive 處理...")
            continue

        # ✅ **獲取 `client_folder_id`**
        client_folder_id = get_gdrive_folder_id(service, root_folder_id, client_folder_name)

        if not client_folder_id:
            logger.warning(f"⚠️ 找不到 `{client_folder_name}`，客戶 `{client_id}` 跳過...")
            continue

        logger.info(f"📂 處理 `{client_id}` 的資料夾 `{client_folder_name}` (ID: {client_folder_id})")

        # ✅ **列出該客戶資料夾內的所有檔案**
        all_files = list_gdrive_files(service, client_folder_id)

        # ✅ **過濾 `_master.xlsx` 檔案**
        master_files = [f for f in all_files if f["file_name"].endswith("_master.xlsx")]

        if not master_files:
            logger.info(f"⚠️ `{client_id}` 沒有 `_master.xlsx` 檔案，跳過...")
            continue

        logger.info(f"✅ `{client_id}` 找到 {len(master_files)} 個 `_master.xlsx` 檔案，開始轉換...")

        for file in master_files:
            xlsx_file_id = file["file_id"]
            xlsx_file_name = file["file_name"]
            sheet_name = xlsx_file_name.replace(".xlsx", "")

            logger.info(f"🔄 轉換 `{xlsx_file_name}` (ID: {xlsx_file_id}) → Google Sheets...")
            google_sheet_id = convert_xlsx_to_google_sheet(service, xlsx_file_id, sheet_name, client_folder_id)

            if google_sheet_id:
                logger.info(f"✅ `{xlsx_file_name}` 轉換成功！Google Sheets ID: {google_sheet_id}")
            else:
                logger.error(f"❌ `{xlsx_file_name}` 轉換失敗！")

    logger.info("🎯 **所有客戶的 `_master.xlsx` 轉換處理完成！**")

if __name__ == "__main__":
    convert_all_clients_master_xlsx()