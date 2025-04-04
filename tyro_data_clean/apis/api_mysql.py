import logging
import pymysql
from app_config import get_config_value, logger

def get_db_connection():
    """🔌 建立 MySQL 連線"""
    try:
        connection = pymysql.connect(
            host=get_config_value(["database", "mysql", "host"]),
            port=int(get_config_value(["database", "mysql", "port"], 3306)),  # 預設 3306
            user=get_config_value(["database", "mysql", "user"]),
            password=get_config_value(["database", "mysql", "password"]),
            database=get_config_value(["database", "mysql", "database"]),  # ✅ 避免 `USE` 問題
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("✅ MySQL 連線成功！")
        return connection
    except pymysql.MySQLError as err:
        logger.error(f"❌ MySQL 連線失敗: {err}")
        return None
    except Exception as err:
        logger.error(f"⚠️ 發生未知錯誤: {err}")
        return None

# ✅ 只有當 `api_mysql.py` 獨立執行時才運行
if __name__ == "__main__":
    logger.info("🚀 開始測試 MySQL 連線...")
    conn = get_db_connection()
    if conn:
        logger.info("✅ MySQL 連線測試成功！")
        conn.close()  # ✅ 測試後關閉連線，避免資源佔用
    else:
        logger.error("❌ MySQL 連線測試失敗！")