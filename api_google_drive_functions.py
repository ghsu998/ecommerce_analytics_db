import io
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from api_google import get_google_drive_service
from app_config import get_config_value, logger

# ✅ 獲取 `Google Drive` 設定
google_server_clients_data_folder_id = get_config_value(["storage", "google_drive", "server_clients_data_folder_id"])

def get_gdrive_folder_id(service, parent_folder_id, folder_name):
    """
    🔍 **搜尋 Google Drive 內的資料夾 ID**
    - `service`: Google Drive API 服務對象
    - `parent_folder_id`: 目標資料夾的上層資料夾 ID
    - `folder_name`: 目標資料夾名稱
    - **回傳**: `folder_id` (成功) 或 `None` (失敗)
    """
    if not parent_folder_id or not folder_name:
        logger.error("❌ `parent_folder_id` 或 `folder_name` 為空，無法搜尋")
        return None

    query = f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    logger.info(f"🔍 搜尋 `{folder_name}`，條件: {query}")

    try:
        response = service.files().list(q=query, fields="files(id, name)").execute()
        folders = response.get("files", [])
        if not folders:
            logger.warning(f"⚠️ `{folder_name}` 不存在於 `{parent_folder_id}` 內")
            return None
        folder_id = folders[0]["id"]
        logger.info(f"✅ 找到 `{folder_name}` (ID: {folder_id})")
        return folder_id
    except HttpError as e:
        logger.error(f"❌ Google Drive API 查詢 `{folder_name}` 失敗: {e}")
        return None

def get_gdrive_file_id(service, folder_id, file_name):
    """
    🔍 **搜尋 Google Drive 內的最新檔案 ID**
    - `service`: Google Drive API 服務對象
    - `folder_id`: 目標檔案的所在資料夾 ID
    - `file_name`: 目標檔案名稱
    - **回傳**: `file_id` (成功) 或 `None` (失敗)
    """
    if not folder_id or not file_name:
        logger.error("❌ `folder_id` 或 `file_name` 為空，無法搜尋")
        return None

    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    logger.info(f"🔍 搜尋 `{file_name}` 於 `{folder_id}`，條件: {query}")

    try:
        response = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc",  # ✅ 確保獲取最新版本
            pageSize=1  # 只取最新的一筆記錄
        ).execute()

        files = response.get("files", [])
        if not files:
            logger.warning(f"⚠️ 找不到 `{file_name}`，請確認檔案是否存在於 `{folder_id}`")
            return None

        latest_file = files[0]  # ✅ 取最新的檔案
        logger.info(f"✅ 找到 `{file_name}`，`file_id`: {latest_file['id']} (最後修改時間: {latest_file['modifiedTime']})")
        return latest_file["id"]

    except HttpError as e:
        logger.error(f"❌ Google Drive API 查詢 `{file_name}` 失敗: {e}")
        return None

def download_gdrive_file_to_memory(service, file_id):
    """
    ⬇️ **從 Google Drive 下載檔案，不存本機，直接返回檔案內容**
    - `service`: Google Drive API 服務對象
    - `file_id`: 目標檔案的 ID
    - **回傳**: `bytes` 檔案內容 (成功) 或 `None` (失敗)
    """
    try:
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        logger.info(f"✅ 檔案 `{file_id}` 下載完成 (記憶體模式)")
        return file_stream.getvalue()
    except HttpError as e:
        logger.error(f"❌ 無法下載 `{file_id}`: {e}")
        return None

def upload_gdrive_file_from_memory(service, folder_id, file_name, file_data, mime_type):
    """
    ⬆️ **上傳或覆蓋 Google Drive 檔案**
    - `service`: Google Drive API 服務對象
    - `folder_id`: 目標資料夾 ID
    - `file_name`: 上傳檔案的名稱
    - `file_data`: 檔案內容 (bytes)
    - `mime_type`: 檔案類型
    - **回傳**: `file_id` (成功) 或 `None` (失敗)
    """
    if not folder_id or not file_name or not file_data:
        logger.error("❌ `folder_id` 或 `file_name` 或 `file_data` 為空，無法上傳")
        return None

    try:
        # 🔍 先檢查檔案是否已存在
        existing_file_id = get_gdrive_file_id(service, folder_id, file_name)
        file_stream = io.BytesIO(file_data)
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)

        if existing_file_id:
            # ✅ 如果檔案已存在，直接更新內容
            file = service.files().update(
                fileId=existing_file_id,
                media_body=media,
                fields="id, modifiedTime"
            ).execute()
            logger.info(f"🔄 檔案 `{file_name}` 已成功覆蓋 (ID: {file.get('id')})")
        else:
            # 🚀 如果檔案不存在，則創建新檔案
            file_metadata = {"name": file_name, "parents": [folder_id]}
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            logger.info(f"✅ 檔案 `{file_name}` 上傳成功 (ID: {file.get('id')})")

        return file.get("id")

    except HttpError as e:
        logger.error(f"❌ 上傳 `{file_name}` 失敗: {e}")
        return None

def list_gdrive_files(service, folder_id):
    """
    📂 **列出 Google Drive 資料夾內的所有檔案**
    - `service`: Google Drive API 服務對象
    - `folder_id`: 目標資料夾 ID
    - **回傳**: `list[dict]` -> `[{ "file_id": "xxx", "file_name": "xxx.xlsx" }, ...]`
    """
    if not folder_id:
        logger.error("❌ `folder_id` 為空，無法列出檔案")
        return []

    query = f"'{folder_id}' in parents and trashed=false"
    logger.info(f"🔍 列出 `{folder_id}` 內的所有檔案 (只包含有效檔案)")

    files_list = []
    page_token = None

    try:
        while True:
            response = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name)",  # ✅ 確保請求包含 "id" 和 "name"
                pageSize=1000,  # ✅ 增加一次請求返回的文件數量
                pageToken=page_token  # ✅ 支援多頁請求
            ).execute()

            files = response.get("files", [])
            if not files:
                logger.warning(f"⚠️ `{folder_id}` 內沒有任何檔案")
                return []

            # ✅ 確保 'name' 鍵存在，避免 KeyError
            for f in files:
                file_id = f.get("id")
                file_name = f.get("name", "UNKNOWN_FILE_NAME")  # 如果 name 缺失，填充預設值
                logger.info(f"📂 {file_name} (ID: {file_id})")
                files_list.append({"file_id": file_id, "file_name": file_name})

            page_token = response.get("nextPageToken")
            if not page_token:
                break  # 沒有更多頁面了

        logger.info(f"✅ 找到 {len(files_list)} 個檔案")
        return files_list

    except HttpError as e:
        logger.error(f"❌ Google Drive API 查詢 `{folder_id}` 內檔案失敗: {e}")
        return []
    
if __name__ == "__main__":
    """
    🚀 **測試 Google Drive API 功能**
    """
    logger.info("🚀 測試 Google Drive API 功能")

    # ✅ **初始化 Google Drive 服務**
    service = get_google_drive_service()
    if not service:
        logger.error("❌ 無法建立 Google Drive 連線，結束測試")
        exit(1)

    # 📂 測試查找資料夾
    folder_name = "client_data_folder_taigers"
    folder_id = get_gdrive_folder_id(service, google_server_clients_data_folder_id, folder_name)

    if folder_id:
        # 🔍 測試查找檔案
        file_name = "tai_inventory_fba_raw_master.xlsx"
        file_id = get_gdrive_file_id(service, folder_id, file_name)

        if file_id:
            # ⬇️ 測試下載檔案
            file_data = download_gdrive_file_to_memory(service, file_id)
            
            if file_data:
                logger.info(f"✅ 找到 `{file_name}`，開始上傳測試")

                # ⬆️ 測試重新上傳
                new_file_name = f"COPY_{file_name}"
                upload_gdrive_file_from_memory(
                    service, folder_id, new_file_name, file_data, 
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # 📂 測試列出資料夾內所有檔案
        logger.info(f"🔍 測試列出 `{folder_name}` 內的所有檔案...")
        file_list = list_gdrive_files(service, folder_id)

        if file_list:
            logger.info(f"📂 `{folder_name}` 內找到 {len(file_list)} 個檔案:")
            for f in file_list:
                logger.info(f"  - {f['file_name']} (ID: {f['file_id']})")

    logger.info("✅ Google Drive API 測試完成！")