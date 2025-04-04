import requests
from app_config import get_config_value, logger  # ✅ 動態讀取 Microsoft 設置

def authenticate_microsoft():
    """📌 取得 OneDrive API Access Token"""
    tenant_id = get_config_value(["authentication", "microsoft", "entra_id", "tenant_id"])
    client_id = get_config_value(["authentication", "microsoft", "entra_id", "client_id"])
    client_secret = get_config_value(["authentication", "microsoft", "entra_id", "client_secret"])

    if not all([tenant_id, client_id, client_secret]):
        logger.error("❌ `app_config.json` 缺少 Microsoft Entra 設定")
        return None

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",  # ✅ 使用應用程式權限，不需要 refresh_token
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()

    if "access_token" in token_data:
        access_token = token_data["access_token"]
        logger.info(f"✅ 取得 Access Token（前 50 碼）：{access_token[:50]}...")
        return access_token
    else:
        logger.error(f"❌ 獲取 Access Token 失敗: {token_data}")
        return None

def get_onedrive_user_drive_id(access_token):
    """
    🔍 **取得 OneDrive User Drive ID**
    - `access_token`: Microsoft Graph API 存取權杖
    - **回傳**: `drive_id` (成功) 或 `None` (失敗)
    """
    user_email = get_config_value(["authentication", "microsoft", "entra_id", "user_email"])

    if not user_email:
        logger.error("❌ `user_email` 未設置，請檢查 `app_config.json`")
        return None

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    token_data = response.json()

    if response.status_code == 200:
        drive_id = token_data.get("id")
        logger.info(f"✅ 取得 OneDrive Drive ID: {drive_id}")
        return drive_id
    else:
        logger.error(f"❌ 獲取 OneDrive Drive ID 失敗: {token_data}")
        return None

if __name__ == "__main__":
    """
    🚀 **測試 Microsoft Graph API 認證**
    - 取得 `access_token`
    - 取得 `drive_id`
    """
    logger.info("🚀 測試 Microsoft Graph API 認證")
    access_token = authenticate_microsoft()

    if access_token:
        drive_id = get_onedrive_user_drive_id(access_token)

    logger.info("✅ Microsoft Graph API 測試完成！")