# tyro_datacenter/utils/datacenter_mapping_config.py

from app_config import logger
from tyro_data_db.mysql_base import get_mysql_connection

def get_datacenter_column_mapping(client_id: str, sheet_tab: str) -> list[dict]:
    """
    🔍 取得指定客戶 + 工作表 tab 的欄位對應設定
    - 來源資料表：`client_datacenter_mapping_table`
    - 回傳格式：[{ "column_name": "sku", "mapped_column": "stock_sku", "is_required": True }, ...]
    """
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT column_name, mapped_column, is_required
            FROM client_datacenter_mapping_table
            WHERE client_id = %s AND sheet_tab = %s
            ORDER BY id ASC
        """
        cursor.execute(query, (client_id, sheet_tab))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows

    except Exception as e:
        logger.error(f"❌ 讀取 Datacenter 欄位對應失敗: {e}")
        return []