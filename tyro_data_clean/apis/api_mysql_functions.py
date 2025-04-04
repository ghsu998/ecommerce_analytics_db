import pymysql
from app_config import get_config_value, logger
from tyro_data_clean.apis.api_mysql import get_db_connection

def get_all_tables():
    """🔍 取得資料庫中的所有表格名稱"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線")
        return []

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
        
        connection.close()

        if tables:
            logger.info(f"✅ 資料庫中的表格: {tables}")
            return tables
        else:
            logger.warning("⚠️ 沒有找到任何表格，請檢查資料庫是否為空！")
            return []
    except Exception as e:
        logger.error(f"❌ 獲取表格失敗: {e}")
        return []


def insert_or_update_data(table, column_names, data_rows, update_columns):
    """✅ **插入或更新數據**"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線，無法插入/更新數據")
        return
    
    columns = ", ".join(column_names)
    placeholders = ", ".join(["%s"] * len(column_names))
    update_clause = ", ".join([f"{col} = VALUES({col})" for col in update_columns])
    
    query = f"""
    INSERT INTO {table} ({columns}) 
    VALUES ({placeholders}) 
    ON DUPLICATE KEY UPDATE {update_clause}
    """

    try:
        with connection.cursor() as cursor:
            cursor.executemany(query, data_rows)
            connection.commit()
            logger.info(f"✅ 成功插入/更新 {cursor.rowcount} 行數據到 {table}")
    except Exception as e:
        logger.error(f"❌ 插入/更新數據失敗: {e}")
    finally:
        connection.close()


def fetch_data(query, params=None):
    """📊 執行 `SELECT` 查詢並返回數據"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線，無法查詢數據")
        return []
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params) if params else cursor.execute(query)
            results = cursor.fetchall()

        connection.close()
        logger.info(f"✅ 成功查詢到 {len(results)} 條數據")
        return results
    except Exception as e:
        logger.error(f"❌ 查詢失敗: {e}")
        return []


def delete_data(table, condition):
    """🗑️ 刪除資料庫中的數據"""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線，無法刪除數據")
        return
    
    query = f"DELETE FROM {table} WHERE {condition}"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            logger.info(f"✅ 成功刪除 {cursor.rowcount} 行數據 from {table}")
    except Exception as e:
        logger.error(f"❌ 刪除數據失敗: {e}")
    finally:
        connection.close()


def get_all_client_ids():
    """
    🔍 **獲取所有客戶 ID**
    - 查詢 `clients_file_mapping_table` 內所有 `client_id`
    """
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線，無法查詢客戶 ID")
        return []

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT DISTINCT client_id FROM clients_file_mapping_table")
            client_ids = [row["client_id"] for row in cursor.fetchall()]

        connection.close()
        logger.info(f"✅ 獲取 {len(client_ids)} 個客戶 ID: {client_ids}")
        return client_ids
    except Exception as e:
        logger.error(f"❌ 無法查詢所有客戶 ID: {e}")
        return []


def get_client_file_mapping_data(client_id):
    """獲取特定 `client_id` 的檔案映射信息"""
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT id, client_id, storage_type, client_data_folder, client_file_prefix, excel_primary_keys
            FROM clients_file_mapping_table
            WHERE client_id = %s
            """
            cursor.execute(query, (client_id,))
            result = cursor.fetchall()
        
        if not result:
            logger.warning(f"⚠️ `{client_id}` 無對應 `clients_file_mapping_table` 設定！")
            return None
        return result
    except Exception as err:
        logger.error(f"❌ 無法查詢 `clients_file_mapping_table` (client_id={client_id})，錯誤: {err}")
        return None
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    """ 🛠️ **獨立測試區塊** """
    logger.info("🚀 開始測試 MySQL Functions...")
    
    tables = get_all_tables()
    if tables:
        logger.info("📂 資料庫表格列表：")
        for table in tables:
            logger.info(f"🗂️ {table}")
    else:
        logger.warning("⚠️ 沒有找到任何表格，請檢查資料庫連接或權限！")