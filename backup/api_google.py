import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from app_config import get_config_value, logger

# ✅ 設定 `token.pickle` 儲存路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
SCOPES = ["https://www.googleapis.com/auth/drive"]

def authenticate_google_cloud():
    """🔑 認證 Google Cloud API 並返回 Credentials"""
    creds = None

    logger.info("🔍 檢查是否已存在 `token.pickle`...")
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)
            logger.info("✅ 讀取已存在的憑據...")
        except (pickle.PickleError, EOFError):
            logger.warning("⚠️ `token.pickle` 文件損壞，刪除並重新認證...")
            os.remove(TOKEN_PATH)
            creds = None

    # ✅ 嘗試刷新過期的 Token
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.info("🔄 Token 已刷新！")
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)  # ✅ 確保刷新後的 Token 被存回去
        except Exception:
            logger.warning("⚠️ 令牌刷新失敗，需重新 OAuth 認證...")
            creds = None

    # ✅ 重新 OAuth 認證
    if not creds:
        try:
            logger.info("📂 讀取 Google Cloud 配置以獲取 OAuth 認證...")
            google_oauth_config = {"installed": get_config_value(["authentication", "google", "cloud"])}
            logger.info("🔑 啟動 OAuth 認證...")
            flow = InstalledAppFlow.from_client_config(google_oauth_config, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)
                logger.info("💾 Token 已保存，未來無需重新認證！")
        except Exception as e:
            logger.critical(f"❌ OAuth 認證失敗，錯誤信息: {e}")
            return None

    return creds

def get_google_drive_service():
    """📂 獲取 Google Drive API 服務對象"""
    logger.info("🔄 嘗試連接 Google Drive API...")
    creds = authenticate_google_cloud()

    if not creds:
        logger.warning("⚠️ 無法建立 Google Drive API 連線，請檢查 OAuth 認證...")
        return None

    try:
        service = build("drive", "v3", credentials=creds)
        logger.info("✅ Google Drive API 連線成功！")
        return service
    except Exception as e:
        logger.error(f"❌ Google Drive API 連線失敗: {e}")
        return None


if __name__ == "__main__":
    """🚀 **測試 Google Drive API 連線**"""
    logger.info("🚀 測試 Google Drive API 連線")
    service = get_google_drive_service()
    
    if service:
        logger.info("✅ 測試成功！Google Drive API 連線成功！")
        print("✅ Google Drive API 連線成功！")
    else:
        logger.error("❌ 測試失敗！無法建立 Google Drive 連線")
        print("❌ Google Drive API 連線失敗！") 