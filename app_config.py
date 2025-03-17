# ### 備註 其他程序調用方式
# from app_config import get_config_value # 獲取 MySQL 設置
# mysql_host = get_config_value(["database", "mysql", "host"])
# mysql_user = get_config_value(["database", "mysql", "user"])
# mysql_password = get_config_value(["database", "mysql", "password"])
# print(f"MySQL Host: {mysql_host}")
# print(f"MySQL User: {mysql_user}")


import logging
import os
import json

# ✅ **獲取 `app_config.json` 絕對路徑**
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_config.json")

# ✅ **動態讀取 `app_config.json`**
def get_config():
    """🔄 確保每次調用都能讀取最新的 `app_config.json` 配置"""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"❌ 找不到 `app_config.json`，請確認文件是否存在於 {CONFIG_PATH}")

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ `app_config.json` 格式錯誤: {e}")

# ✅ **輔助函數：獲取指定配置值**
def get_config_value(keys, default=None):
    """
    🔍 從 `app_config.json` 中獲取嵌套配置值
    - `keys`: 例如 `["database", "mysql", "host"]`
    - `default`: 如果鍵不存在時的預設值
    """
    config = get_config()
    value = config
    for key in keys:
        value = value.get(key, default) if isinstance(value, dict) else default
    return value

# ✅ **全局日誌系統**
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

if not os.path.exists(logs_dir):
    try:
        os.makedirs(logs_dir)
    except PermissionError:
        raise PermissionError(f"❌ 沒有權限創建 `{logs_dir}`，請檢查權限")

log_file = os.path.join(logs_dir, "full_logging.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("✅ `app_config.py` 已加載全局配置和日誌系統！")

# ✅ **測試讀取關鍵變數**
try:
    logger.info(f"📂 Google Server Data Folder ID: {get_config_value(['storage', 'google_drive', 'server_data_folder_id'])}")
    logger.info(f"📂 Google Server Clients Data Folder ID: {get_config_value(['storage', 'google_drive', 'server_clients_data_folder_id'])}")
    logger.info(f"📂 OneDrive Server Data Folder ID: {get_config_value(['storage', 'onedrive', 'server_data_folder_id'])}")
    logger.info(f"📂 OneDrive Server Clients Data Folder ID: {get_config_value(['storage', 'onedrive', 'server_clients_data_folder_id'])}")
except Exception as e:
    logger.error(f"❌ 無法加載 `app_config.json`: {e}")