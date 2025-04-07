# tyro_data_clean/utils/client_info.py

from tyro_data_clean.apis.api_mysql import get_db_connection  # ✅ 你的 MySQL 抽象層
from app_config import logger
import pymysql

def get_client_name_by_id(client_id: str) -> str:
    """
    根據 client_id 從 clients_info_table 查詢 client_name
    """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT client_name FROM clients_info_table WHERE client_id = %s LIMIT 1"
            cursor.execute(sql, (client_id,))
            result = cursor.fetchone()
            return result["client_name"] if result else "Unknown"
    except Exception as err:
        logger.error(f"❌ 查詢 client_name 失敗（client_id={client_id}），錯誤: {err}")
        return "Unknown"
    finally:
        if connection:
            connection.close()