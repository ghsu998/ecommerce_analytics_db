# ecommerce_analytics_db/tyro_data_db/db_connection.py

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
            database=get_config_value(["database", "mysql", "database"]),
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
