import io
from openpyxl import Workbook
from app_config import logger
from tyro_data_clean.apis.api_google_drive_functions import (
    get_gdrive_folder_id, list_gdrive_files, upload_gdrive_file_from_memory
)
from tyro_data_clean.apis.api_microsoft_onedrive_functions import (
    get_onedrive_folder_id, list_onedrive_files, upload_onedrive_file
)
from app_config import get_config_value
from tyro_data_clean.utils import client_file_mapping_config

def generate_datacenter_filename(client_name: str) -> str:
    prefix = client_name.strip().split()[0]
    return f"{prefix}_datacenter.xlsx"

def create_excel_file_bytes() -> bytes:
    wb = Workbook()
    wb.active.title = "Data_Inventory_Clean"
    wb.create_sheet("Data_Sales_Clean")
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream.getvalue()

def ensure_datacenter_file_exists(client_id: str, client_name: str, storage_type: str):
    filename = generate_datacenter_filename(client_name)
    folder_base_id = get_config_value(["storage", storage_type, "server_clients_data_folder_id"])

    # ✅ 從 mapping 設定取得 client 的資料夾名稱
    client_info = client_file_mapping_config.get_client_data_settings(client_id)
    if not client_info:
        logger.warning(f"⚠️ `{client_id}` 沒有對應的 mapping 設定，跳過 DataCenter 建立")
        return

    client_data_folder = client_info["client_data_folder"]

    # ✅ 判斷平台並取得雲端資料夾與檔案清單
    if storage_type == "google_drive":
        service = get_gdrive_service_for_check()
        folder_id = get_gdrive_folder_id(service, folder_base_id, client_data_folder)
        files = list_gdrive_files(service, folder_id) if folder_id else []
    else:
        service = get_onedrive_service_for_check()
        folder_id = get_onedrive_folder_id(service, folder_base_id, client_data_folder)
        files = list_onedrive_files(service, folder_id) if folder_id else []

    if not folder_id:
        logger.warning(f"⚠️ `{client_id}` 無法取得 `{client_data_folder}` 雲端資料夾，跳過 DataCenter 建立")
        return

    # ✅ 檢查是否已存在 DataCenter.xlsx
    existing = [f for f in files if f["file_name"] == filename]
    if existing:
        logger.info(f"[Tyro] ⏩ 已存在 DataCenter: {filename}")
        return

    # ✅ 建立檔案並上傳
    file_bytes = create_excel_file_bytes()

    if storage_type == "google_drive":
        upload_gdrive_file_from_memory(
            service=service,
            folder_id=folder_id,
            file_name=filename,
            file_data=file_bytes,
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        upload_onedrive_file(
            service=service,
            folder_id=folder_id,
            file_name=filename,
            file_bytes=file_bytes
        )

    logger.info(f"[Tyro] ✅ 已建立 DataCenter 檔案於 {storage_type}: {filename}")

# 🔧 提供 local 模組用快速服務
def get_gdrive_service_for_check():
    from tyro_data_clean.apis.api_google import get_google_drive_service
    return get_google_drive_service()

def get_onedrive_service_for_check():
    from tyro_data_clean.apis.api_microsoft import authenticate_microsoft
    return authenticate_microsoft()