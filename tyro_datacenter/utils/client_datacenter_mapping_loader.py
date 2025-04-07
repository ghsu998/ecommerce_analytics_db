# tyro_datacenter/utils/client_datacenter_mapping_loader.py

import pandas as pd
from app_config import logger, get_config_value
from tyro_data_clean.utils.client_file_mapping_config import get_clients_list, get_client_data_settings
from tyro_data_db.mysql_base import insert_or_ignore_datacenter_mapping
from tyro_data_clean.apis.api_google_drive_functions import (
    get_gdrive_folder_id, list_gdrive_files, download_google_sheet_as_dataframe, get_google_drive_service
)
from tyro_data_clean.apis.api_microsoft_onedrive_functions import (
    get_onedrive_folder_id, list_onedrive_files, download_onedrive_file
)
from tyro_data_clean.apis.api_microsoft import authenticate_microsoft
from tyro_data_clean.utils.excel_reader import read_excel_bytes_tab

SUPPORTED_TABS = ["Data_Inventory_Clean", "Data_Sales_Clean"]

def extract_columns_from_sheet(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if col and str(col).strip() != ""]

def parse_client_datacenter_columns(client_id: str):
    client_info = get_client_data_settings(client_id)
    if not client_info:
        logger.warning(f"⚠️ 找不到 `{client_id}` 設定，跳過")
        return

    storage_type = client_info["storage_type"]
    client_folder_name = client_info["client_data_folder"]
    filename_prefix = client_folder_name.split('_')[-1]
    datacenter_file_base = f"{filename_prefix}_datacenter"

    logger.info(f"🔍 處理 `{client_id}` - 來源檔案: `{datacenter_file_base}`")

    if storage_type == "google_drive":
        service = get_google_drive_service()
        root_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])
        folder_id = get_gdrive_folder_id(service, root_folder_id, client_folder_name)
        files = list_gdrive_files(service, folder_id)

        # ✅ 找出轉換後的 Google Sheets（名稱完全相符）
        datacenter_file = next((f for f in files if f["file_name"] == datacenter_file_base), None)
        if not datacenter_file:
            logger.warning(f"❌ `{datacenter_file_base}` Google Sheets 檔案不存在，跳過...")
            return

        for tab in SUPPORTED_TABS:
            df = download_google_sheet_as_dataframe(service, datacenter_file["file_id"], tab)
            if df is not None:
                for col in extract_columns_from_sheet(df):
                    insert_or_ignore_datacenter_mapping(client_id, tab, col)

    elif storage_type == "onedrive":
        token = authenticate_microsoft()
        root_folder_id = get_config_value(["storage", "onedrive", "server_clients_data_folder_id"])
        folder_id = get_onedrive_folder_id(token, root_folder_id, client_folder_name)
        files = list_onedrive_files(token, folder_id)

        datacenter_file = next((f for f in files if f["file_name"] == f"{datacenter_file_base}.xlsx"), None)
        if not datacenter_file:
            logger.warning(f"❌ `{datacenter_file_base}.xlsx` OneDrive 檔案不存在，跳過...")
            return

        file_bytes = download_onedrive_file(token, datacenter_file["file_id"])
        if not file_bytes:
            return

        for tab in SUPPORTED_TABS:
            df = read_excel_bytes_tab(file_bytes, tab)
            if df is not None:
                for col in extract_columns_from_sheet(df):
                    insert_or_ignore_datacenter_mapping(client_id, tab, col)

def sync_all_clients_datacenter_columns():
    clients = get_clients_list()
    logger.info(f"🔁 開始解析 {len(clients)} 個客戶的 DataCenter 欄位...")
    for client_id in clients:
        parse_client_datacenter_columns(client_id)
    logger.info("✅ 欄位同步完成！")

if __name__ == "__main__":
    sync_all_clients_datacenter_columns()