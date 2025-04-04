import requests
from app_config import get_config_value, logger
from tyro_data_clean.apis.api_microsoft import authenticate_microsoft

# ✅ 獲取 `OneDrive` 設定
onedrive_server_clients_data_folder_id = get_config_value(["storage", "onedrive", "server_clients_data_folder_id"])
user_email = get_config_value(["authentication", "microsoft", "entra_id", "user_email"])

if not onedrive_server_clients_data_folder_id:
    logger.error("❌ `onedrive_server_clients_data_folder_id` 未設置，請確認 `app_config.json`")
    exit()

def get_onedrive_folder_id(access_token, parent_folder_id, folder_name):
    """
    🔍 **在 OneDrive Business 裡查找 `folder_name`**
    - **`parent_folder_id`**: 父資料夾的 ID (可以是根目錄)
    - **`folder_name`**: 要查找的資料夾名稱
    - **回傳**: `folder_id` (成功) 或 `None` (失敗)
    """
    if not parent_folder_id:
        logger.error("❌ `parent_folder_id` 未設置")
        return None

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{parent_folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        folders = response.json().get("value", [])
        for folder in folders:
            if folder.get("name") == folder_name and "folder" in folder:
                logger.info(f"✅ 找到 OneDrive 資料夾 `{folder_name}` (ID: {folder['id']})")
                return folder["id"]

        logger.warning(f"⚠️ 無法找到 OneDrive 資料夾 `{folder_name}` 於 `{parent_folder_id}` 內")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OneDrive API 查詢 `{folder_name}` 失敗: {e}")
        return None

def get_onedrive_file_id(access_token, folder_id, file_name):
    """
    🔍 **搜尋 OneDrive 內的檔案 ID**
    - `access_token`: Microsoft Graph API 存取權杖
    - `folder_id`: 目標檔案的所在資料夾 ID
    - `file_name`: 目標檔案名稱
    - **回傳**: `file_id` (成功) 或 `None` (失敗)
    """
    if not all([access_token, folder_id, file_name]):
        logger.error("❌ `access_token`, `folder_id` 或 `file_name` 為空，無法搜尋")
        return None

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json().get("value", [])

        for file in files:
            if file["name"] == file_name:
                logger.info(f"✅ 找到 `{file_name}`，`file_id`: {file['id']}")
                return file["id"]

        logger.warning(f"⚠️ `{file_name}` 不存在於 `{folder_id}` 內")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OneDrive API 查詢 `{file_name}` 失敗: {e}")
        return None

def download_onedrive_file(access_token, file_id):
    """
    ⬇️ **從 OneDrive 下載檔案，不存本機，直接返回檔案內容**
    - `access_token`: Microsoft Graph API 存取權杖
    - `file_id`: 目標檔案的 ID
    - **回傳**: `bytes` 檔案內容 (成功) 或 `None` (失敗)
    """
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/content"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*"
    }

    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        logger.info(f"✅ 檔案 `{file_id}` 下載成功")
        return response.content
    else:
        logger.error(f"❌ 下載 OneDrive 檔案 `{file_id}` 失敗: {response.status_code} - {response.text}")
        return None
    
def upload_onedrive_file(access_token, parent_folder_id, file_name, file_data):
    """
    ⬆️ **直接將記憶體中的資料上傳到 OneDrive，並覆蓋同名檔案**
    - `access_token`: Microsoft Graph API 存取權杖
    - `parent_folder_id`: 目標資料夾 ID
    - `file_name`: 上傳檔案的名稱
    - `file_data`: 檔案內容 (bytes)
    - `user_email`: OneDrive 用戶 Email
    - **回傳**: `file_id` (成功) 或 `None` (失敗)
    """
    if not all([access_token, parent_folder_id, file_name, file_data, user_email]):
        logger.error("❌ `access_token`, `parent_folder_id`, `file_name`, `file_data` 或 `user_email` 為空，無法上傳")
        return None

    # 📌 設定 API URL：使用 `:/content` 來確保覆蓋同名檔案
    
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{parent_folder_id}:/{file_name}:/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }

    try:
        # 使用 PUT 方法，OneDrive 會自動覆蓋同名檔案
        response = requests.put(url, headers=headers, data=file_data)
        response.raise_for_status()  # 確保請求成功

        file_id = response.json().get("id")
        logger.info(f"✅ 檔案 `{file_name}` 上傳並覆蓋成功 (ID: {file_id})")
        return file_id

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 上傳 OneDrive 檔案 `{file_name}` 失敗: {e}")
        return None

def list_onedrive_files(access_token, folder_id):
    """
    📂 **列出 OneDrive Business 資料夾內的所有檔案**
    - `access_token`: Microsoft Graph API 存取權杖
    - `folder_id`: 目標資料夾 ID
    - **回傳**: `list[dict]` -> `[{ "file_id": "xxx", "file_name": "xxx.xlsx" }, ...]`
    """
    if not all([access_token, folder_id]):
        logger.error("❌ `access_token` 或 `folder_id` 為空，無法列出檔案")
        return []

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        files = response.json().get("value", [])

        if not files:
            logger.warning(f"⚠️ `{folder_id}` 內沒有任何檔案")
            return []

        file_list = [{"file_id": f["id"], "file_name": f["name"]} for f in files]
        logger.info(f"✅ `{folder_id}` 內找到 {len(file_list)} 個檔案")
        return file_list
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ OneDrive API 查詢 `{folder_id}` 內檔案失敗: {e}")
        return []

if __name__ == "__main__":
    """
    🚀 **測試 OneDrive API 功能**
    - 取得 `access_token`
    - 取得 `folder_id`
    - 取得 `file_id`
    - 測試 `list_onedrive_files()`
    - 測試下載 & 上傳檔案
    """
    logger.info("🚀 測試 OneDrive API 功能")
    
    # ✅ **1. 取得 Access Token**
    access_token = authenticate_microsoft()
    if not access_token:
        logger.error("❌ 無法獲取 Access Token，結束測試")
        exit(1)

    # ✅ **2. 取得 OneDrive `folder_id`**
    parent_folder_id = onedrive_server_clients_data_folder_id
    folder_name = "client_data_folder_kinger"  # 測試的 OneDrive 目標資料夾
    folder_id = get_onedrive_folder_id(access_token, parent_folder_id, folder_name)

    if folder_id:
        # ✅ **3. 測試 `list_onedrive_files()`**
        files = list_onedrive_files(access_token, folder_id)
        logger.info(f"📂 `{folder_name}` 內的檔案列表: {files}")

        # ✅ **4. 測試查找檔案**
        file_name = "kinger_data_daily_sales_raw_master.xlsx"  # 測試檔案名稱
        file_id = get_onedrive_file_id(access_token, folder_id, file_name)

        # ✅ **5. 測試下載檔案**
        if file_id:
            file_data = download_onedrive_file(access_token, file_id)
            if file_data:
                logger.info(f"📂 檔案 `{file_name}` 下載成功，大小: {len(file_data)} bytes")

                # ✅ **6. 測試上傳檔案**
                new_file_name = f"COPY_{file_name}"
                upload_result = upload_onedrive_file(access_token, folder_id, new_file_name, file_data)
                if upload_result:
                    logger.info(f"✅ 檔案 `{new_file_name}` 上傳成功！")

    logger.info("✅ OneDrive API 測試完成！")