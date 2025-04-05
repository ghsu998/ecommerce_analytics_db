from app_config import get_config_value, logger
from tyro_data_clean.utils.client_file_mapping_config import get_clients_list, get_client_data_settings
from tyro_data_clean.apis.api_google_drive_functions import (
    convert_xlsx_to_google_sheet, get_google_drive_service, 
    list_gdrive_files, get_gdrive_folder_id
)

def convert_all_clients_master_xlsx():
    """
    🔄 將所有客戶的 `_master.xlsx` 檔案轉換為 Google Sheets（覆蓋式轉換）
    - 來源：Google Drive 每個客戶資料夾內的 Excel 檔
    - 只處理 storage_type = google_drive 的客戶
    - 不建立新檔，而是覆蓋原始 `_master.xlsx` 所對應的 Google Sheets
    """
    service = get_google_drive_service()
    if not service:
        logger.error("❌ Google Drive API 服務無法連接")
        return

    clients = get_clients_list()
    if not clients:
        logger.warning("⚠️ 沒有找到任何客戶，請確認 `clients_file_mapping_table` 是否正確")
        return

    logger.info(f"🔍 開始處理 {len(clients)} 個客戶的 `_master.xlsx` 檔案...")

    root_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])

    for client_id in clients:
        convert_client_master_xlsx(client_id, root_folder_id, service)

    logger.info("🎯 **所有客戶的 `_master.xlsx` 轉換處理完成！**")

def convert_client_master_xlsx(client_id, root_folder_id, service):
    client_info = get_client_data_settings(client_id)
    if not client_info:
        logger.warning(f"⚠️ 客戶 `{client_id}` 設置錯誤，跳過...")
        return

    client_folder_name = client_info["client_data_folder"]
    storage_type = client_info["storage_type"]

    if storage_type.lower() != "google_drive":
        logger.warning(f"⚠️ `{client_id}` 使用的是 `{storage_type}`，跳過 Google Drive 處理...")
        return

    client_folder_id = get_gdrive_folder_id(service, root_folder_id, client_folder_name)
    if not client_folder_id:
        logger.warning(f"⚠️ 找不到 `{client_folder_name}`，客戶 `{client_id}` 跳過...")
        return

    logger.info(f"📂 處理 `{client_id}` 的資料夾 `{client_folder_name}` (ID: {client_folder_id})")

    all_files = list_gdrive_files(service, client_folder_id)
    master_files = [f for f in all_files if f["file_name"].endswith("_master.xlsx")]

    if not master_files:
        logger.info(f"⚠️ `{client_id}` 沒有 `_master.xlsx` 檔案，跳過...")
        return

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

def convert_single_client_master_xlsx(client_id):
    """
    🔄 單一客戶版本：將 `_master.xlsx` 檔案轉換為 Google Sheets（覆蓋式轉換）
    """
    service = get_google_drive_service()
    if not service:
        logger.error("❌ Google Drive API 服務無法連接")
        return

    client_info = get_client_data_settings(client_id)
    if not client_info or client_info.get("storage_type") != "google_drive":
        logger.warning(f"⚠️ `{client_id}` 非 Google Drive 客戶，跳過轉換")
        return

    client_folder_name = client_info["client_data_folder"]
    root_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])
    client_folder_id = get_gdrive_folder_id(service, root_folder_id, client_folder_name)

    if not client_folder_id:
        logger.warning(f"⚠️ 找不到 `{client_folder_name}`，客戶 `{client_id}` 跳過...")
        return

    logger.info(f"📂 單客戶模式：轉換 `{client_id}` 資料夾 `{client_folder_name}`")

    all_files = list_gdrive_files(service, client_folder_id)
    master_files = [f for f in all_files if f["file_name"].endswith("_master.xlsx")]

    if not master_files:
        logger.info(f"⚠️ `{client_id}` 沒有 `_master.xlsx` 檔案，跳過")
        return

    for file in master_files:
        xlsx_file_id = file["file_id"]
        xlsx_file_name = file["file_name"]
        sheet_name = xlsx_file_name.replace(".xlsx", "")

        logger.info(f"🔄 轉換 `{xlsx_file_name}` → Google Sheets")
        google_sheet_id = convert_xlsx_to_google_sheet(service, xlsx_file_id, sheet_name, client_folder_id)

        if google_sheet_id:
            logger.info(f"✅ `{xlsx_file_name}` 轉換成功！Google Sheets ID: {google_sheet_id}")
        else:
            logger.error(f"❌ `{xlsx_file_name}` 轉換失敗")


# ✅ 給 main.py 單一客戶調用
def main(client_id, config):
    service = get_google_drive_service()
    root_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])
    convert_client_master_xlsx(client_id, root_folder_id, service)

# ✅ CLI 單獨測試時使用
if __name__ == "__main__":
    convert_all_clients_master_xlsx()
