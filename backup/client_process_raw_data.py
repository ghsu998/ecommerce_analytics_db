import io
import pandas as pd
import re
from datetime import datetime
from app_config import get_config_value, logger
from app_utility import clean_column_names, format_date_columns
from client_file_mapping_config import get_client_data_settings, get_clients_list
from api_google_drive_functions import (
    get_gdrive_folder_id, get_gdrive_file_id, download_gdrive_file_to_memory, 
    upload_gdrive_file_from_memory, list_gdrive_files, get_google_drive_service
)
from api_microsoft_onedrive_functions import (
    get_onedrive_folder_id, get_onedrive_file_id, download_onedrive_file, 
    upload_onedrive_file, list_onedrive_files, authenticate_microsoft
)

TEST_MODE = False
TEST_CLIENTS = ["client_001", "client_003"]

def extract_dates_from_filename(filename):
    """
    🔍 從文件名稱解析 `db_start_date` 和 `db_end_date`
    - 允許 `prefix_YYYY_MM_DD.xlsx`（1 個日期）
    - 允許 `prefix_YYYY_MM_DD_YYYY_MM_DD.xlsx`（2 個日期）
    """
    date_pattern = re.findall(r"(\d{4}_\d{2}_\d{2})", filename)
    
    if len(date_pattern) == 1:
        return None, date_pattern[0].replace("_", "-")
    elif len(date_pattern) == 2:
        return date_pattern[0].replace("_", "-"), date_pattern[1].replace("_", "-")
    
    return None, None

def process_client_raw_data(client_id, storage_type, service, user_email):
    client_info = get_client_data_settings(client_id)
    if not client_info:
        logger.error(f"❌ `{client_id}` 設置錯誤，無法繼續")
        return

    client_data_folder = client_info["client_data_folder"]
    client_primary_keys = client_info["files"]

    logger.info(f"📂 開始處理 `{client_id}` - 目標資料夾: {client_data_folder}")

    if storage_type == "google_drive":
        parent_folder_id = get_gdrive_folder_id(service, get_config_value(["storage", "google_drive", "server_clients_data_folder_id"]), client_data_folder)
    else:
        access_token = authenticate_microsoft()
        parent_folder_id = get_onedrive_folder_id(access_token, get_config_value(["storage", "onedrive", "server_clients_data_folder_id"]), client_data_folder)

    if not parent_folder_id:
        logger.error(f"❌ `{client_id}` - 無法找到 `{client_data_folder}`")
        return

    total_files = 0
    matching_files = 0
    non_matching_files = 0

    logger.info(f"🔍 開始列出 `{client_id}` 目錄內的檔案...")
    all_files = list_gdrive_files(service, parent_folder_id) if storage_type == "google_drive" else list_onedrive_files(service, parent_folder_id)
    total_files = len(all_files)

    for file_prefix, primary_keys in client_primary_keys.items():
        if not isinstance(primary_keys, list):
            logger.warning(f"⚠️ `{client_id}` - `client_file_primary_keys` 應該是列表格式，跳過 `{file_prefix}`")
            continue

        regex_pattern = rf"^{file_prefix}_(\d{{4}}_\d{{2}}_\d{{2}})(?:_(\d{{4}}_\d{{2}}_\d{{2}}))?\.xlsx$"
        filtered_files = [f for f in all_files if re.match(regex_pattern, f["file_name"])]

        matching_files += len(filtered_files)
        non_matching_files += total_files - len(filtered_files)

        logger.info(f"📊 `{client_id}` - `{file_prefix}` 總檔案數: {total_files}, ✅ 符合: {len(filtered_files)}, ⚠️ 不符合: {total_files - len(filtered_files)}")

        if not filtered_files:
            logger.warning(f"⚠️ `{client_id}` - 沒有符合 `{file_prefix}_YYYY_MM_DD.xlsx` 格式的檔案")
            continue

        # 開始下載、處理、合併、上傳
        df_list = []
        for raw_file in filtered_files:
            file_data = download_gdrive_file_to_memory(service, raw_file["file_id"]) if storage_type == "google_drive" else download_onedrive_file(service, raw_file["file_id"])

            if file_data:
                df = pd.read_excel(io.BytesIO(file_data))
                df = clean_column_names(df)
                db_start_date, db_end_date = extract_dates_from_filename(raw_file["file_name"])

                if "db_start_date" in primary_keys and db_start_date:
                    df["db_start_date"] = db_start_date
                if "db_end_date" in primary_keys and db_end_date:
                    df["db_end_date"] = db_end_date

                df = format_date_columns(df)

                output = io.BytesIO()
                df.to_excel(output, index=False, engine='xlsxwriter')
                output.seek(0)

                if storage_type == "google_drive":
                    upload_gdrive_file_from_memory(service, parent_folder_id, raw_file["file_name"], output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    upload_onedrive_file(service, parent_folder_id, raw_file["file_name"], output.getvalue())

                df_list.append(df)

        if df_list:
            df_raw_combined = pd.concat(df_list, ignore_index=True)
            
            # **這裡額外清理合併後的 df 欄位名稱**
            df_raw_combined = clean_column_names(df_raw_combined)
            
            df_raw_combined.drop_duplicates(subset=primary_keys, inplace=True)

            output = io.BytesIO()
            df_raw_combined.to_excel(output, index=False, engine='xlsxwriter')
            output.seek(0)

            master_filename = f"{file_prefix}_master.xlsx"
            if storage_type == "google_drive":
                upload_gdrive_file_from_memory(service, parent_folder_id, master_filename, output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                upload_onedrive_file(service, parent_folder_id, master_filename, output.getvalue())

            logger.info(f"✅ `{client_id}` - `{master_filename}` 更新成功")

    logger.info(f"📊 `{client_id}` - **處理完成**: 總檔案: {total_files}, ✅ 符合: {matching_files}, ⚠️ 不符合: {non_matching_files}")

def main():
    clients = TEST_CLIENTS if TEST_MODE else get_clients_list()
    if not clients:
        logger.error("❌ 無客戶可處理，請確認 `clients_file_mapping_table` 有數據")
        return

    logger.info(f"🚀 開始處理 {len(clients)} 個客戶數據...")
    google_service = get_google_drive_service()
    microsoft_token = authenticate_microsoft()

    for client_id in clients:
        client_info = get_client_data_settings(client_id)
        storage_type = client_info.get("storage_type", "google_drive")  # 預設 Google Drive
        service = google_service if storage_type == "google_drive" else microsoft_token
        process_client_raw_data(client_id, storage_type, service, None)
        logger.info("🎯 **所有客戶數據處理完成！**")

if __name__ == "__main__":
    main()
