
import sys, os
import io
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

from app_config import get_config_value, logger
from tyro_data_clean.utils import app_utility
from tyro_data_clean.utils import client_file_mapping_config
from tyro_data_clean.apis.api_google_drive_functions import (
    get_gdrive_folder_id, list_gdrive_files, download_gdrive_file_to_memory,
    upload_gdrive_file_from_memory, get_google_drive_service
)
from tyro_data_clean.apis.api_microsoft_onedrive_functions import (
    get_onedrive_folder_id, list_onedrive_files, download_onedrive_file,
    upload_onedrive_file, authenticate_microsoft
)


def get_primary_keys_from_config(primary_keys_config) -> list:
    """
    根據 config 提供的 list 或 str 自動格式化為 primary_keys list
    """
    if isinstance(primary_keys_config, list):
        return [key.strip() for key in primary_keys_config]
    elif isinstance(primary_keys_config, str):
        return [key.strip() for key in primary_keys_config.split(",")]
    else:
        return []


def extract_dates_from_filename(filename):
    date_pattern = re.findall(r"(\d{4}_\d{2}_\d{2})", filename)
    if len(date_pattern) == 1:
        return None, date_pattern[0].replace("_", "-")
    elif len(date_pattern) == 2:
        return date_pattern[0].replace("_", "-"), date_pattern[1].replace("_", "-")
    return None, None

def process_client_raw_data(client_id, storage_type, service, user_email):
    client_info = client_file_mapping_config.get_client_data_settings(client_id)
    if not client_info:
        logger.error(f"❌ `{client_id}` 設置錯誤，無法繼續")
        return

    client_data_folder = client_info["client_data_folder"]
    client_primary_keys = client_info["files"]

    logger.info(f"📂 開始處理 `{client_id}` - 目標資料夾: {client_data_folder}")

    if storage_type == "google_drive":
        parent_folder_id = get_gdrive_folder_id(service, get_config_value(["storage", "google_drive", "server_clients_data_folder_id"]), client_data_folder)
    else:
        parent_folder_id = get_onedrive_folder_id(service, get_config_value(["storage", "onedrive", "server_clients_data_folder_id"]), client_data_folder)

    if not parent_folder_id:
        logger.error(f"❌ `{client_id}` - 無法找到 `{client_data_folder}`")
        return

    logger.info(f"🔍 開始列出 `{client_id}` 目錄內的檔案...")
    all_files = list_gdrive_files(service, parent_folder_id) if storage_type == "google_drive" else list_onedrive_files(service, parent_folder_id)
    total_files = len(all_files)

    matching_files = 0
    non_matching_files = 0

    for file_prefix, primary_keys in client_primary_keys.items():
        if not isinstance(primary_keys, list):
            logger.warning(f"⚠️ `{client_id}` - `client_file_primary_keys` 應該是列表格式，跳過 `{file_prefix}`")
            continue

        def normalize_name(name):
            return name.replace("-", "_")

        regex_pattern = rf"^{normalize_name(file_prefix)}_(\d{{4}}_\d{{2}}_\d{{2}})(?:_(\d{{4}}_\d{{2}}_\d{{2}}))?\.xlsx$"
        filtered_files = [f for f in all_files if re.match(regex_pattern, normalize_name(f["file_name"]))]

        matching_files += len(filtered_files)
        non_matching_files += total_files - len(filtered_files)

        logger.info(f"📊 `{client_id}` - `{file_prefix}` 總檔案數: {total_files}, ✅ 符合: {len(filtered_files)}, ⚠️ 不符合: {total_files - len(filtered_files)}")

        if not filtered_files:
            logger.warning(f"⚠️ `{client_id}` - 沒有符合 `{file_prefix}_YYYY_MM_DD.xlsx` 格式的檔案")
            continue

        df_list = []
        for raw_file in filtered_files:
            file_data = download_gdrive_file_to_memory(service, raw_file["file_id"]) if storage_type == "google_drive" else download_onedrive_file(service, raw_file["file_id"])

            if file_data:
                df = pd.read_excel(io.BytesIO(file_data))
                df = app_utility.clean_column_names(df)
                db_start_date, db_end_date = extract_dates_from_filename(raw_file["file_name"])

                if "db_start_date" in primary_keys and db_start_date:
                    df["db_start_date"] = db_start_date
                if "db_end_date" in primary_keys and db_end_date:
                    df["db_end_date"] = db_end_date

                df = app_utility.format_date_columns(df)
                df_list.append(df)

        if df_list:
            df_raw_combined = pd.concat(df_list, ignore_index=True)
            df_raw_combined = app_utility.clean_column_names(df_raw_combined)

            master_filename = f"{file_prefix}_master.xlsx"
            old_master_df = None
            existing_master_file = next((f for f in all_files if f["file_name"] == master_filename), None)
            if existing_master_file:
                master_data = download_gdrive_file_to_memory(service, existing_master_file["file_id"]) if storage_type == "google_drive" else download_onedrive_file(service, existing_master_file["file_id"])
                try:
                    old_master_df = pd.read_excel(io.BytesIO(master_data))
                    old_master_df = app_utility.clean_column_names(old_master_df)
                except Exception as e:
                    logger.warning(f"⚠️ `{client_id}` - 無法讀取舊 master `{master_filename}`: {str(e)}")

            # ⚙️ 合併與去重：使用 config 中定義的 primary keys
            if old_master_df is not None:
                df_merged = pd.concat([old_master_df, df_raw_combined], ignore_index=True)
                dedup_keys = get_primary_keys_from_config(primary_keys)
                df_merged.drop_duplicates(subset=dedup_keys, keep="last", inplace=True)
            else:
                df_merged = df_raw_combined

            # 💾 儲存合併結果
            output = io.BytesIO()
            df_merged.to_excel(output, index=False, engine='xlsxwriter')
            output.seek(0)

            if storage_type == "google_drive":
                upload_gdrive_file_from_memory(service, parent_folder_id, master_filename, output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                upload_onedrive_file(service, parent_folder_id, master_filename, output.getvalue())

            logger.info(f"✅ `{client_id}` - `{master_filename}` 更新成功（已合併並保留歷史紀錄）")

    logger.info(f"📊 `{client_id}` - **處理完成**: 總檔案: {total_files}, ✅ 符合: {matching_files}, ⚠️ 不符合: {non_matching_files}")

def main():
    clients = client_file_mapping_config.get_clients_list()
    for client_id in clients:
        print(f"\n🔁 處理中: {client_id}")
        process_client_data(client_id)
        upload_master_to_sheet(client_id)

def process_client_data(client_id):
    client_info = client_file_mapping_config.get_client_data_settings(client_id)
    if not client_info:
        print(f"❌ 無法取得 `{client_id}` 的資料設置，跳過處理")
        return

    storage_type = client_info.get("storage_type", "google_drive")
    service = get_google_drive_service() if storage_type == "google_drive" else authenticate_microsoft()

    process_client_raw_data(
        client_id=client_id,
        storage_type=storage_type,
        service=service,
        user_email=None
    )

def upload_master_to_sheet(client_id):
    client_info = client_file_mapping_config.get_client_data_settings(client_id)
    if not client_info or client_info.get("storage_type") != "google_drive":
        return
    from tyro_data_clean.utils import client_file_xlsx_convert_google_sheet
    client_file_xlsx_convert_google_sheet.convert_single_client_master_xlsx(client_id)

if __name__ == "__main__":
    main()
