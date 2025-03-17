import requests
from app_config import microsoft_entra_config

# 取得 Microsoft Entra API 憑證
client_id = microsoft_entra_config.get("client_id")
client_secret = microsoft_entra_config.get("client_secret")
tenant_id = microsoft_entra_config.get("tenant_id")

# 構建 Token 請求 URL
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

# 設定請求參數，包含 offline_access 來獲取 refresh_token
payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "https://graph.microsoft.com/.default offline_access",
    "grant_type": "client_credentials"
}

# 發送 POST 請求以獲取 Access Token 和 Refresh Token
response = requests.post(token_url, data=payload)

# 檢查 API 回應
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    print("✅ Access Token:", access_token[:50] + "...")  # 顯示前 50 碼，避免資訊洩漏
    if refresh_token:
        print("✅ Refresh Token:", refresh_token[:50] + "...")
    else:
        print("⚠️ 無法獲取 Refresh Token，請確認 Azure AD 權限")

else:
    print("❌ 無法取得 Token，錯誤訊息:", response.text)