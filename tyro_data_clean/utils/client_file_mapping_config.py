import logging
import pandas as pd
import pymysql
import json
from tabulate import tabulate

from app_config import get_config_value, logger  # ✅ 確保從 `app_config.py` 讀取配置
from tyro_data_clean.utils.app_utility import clean_column_names  # ✅ 確保 `client_file_primary_keys` 一致
from tyro_data_clean.apis.api_mysql import get_db_connection  # ✅ 確保 MySQL 連線函數可用

# ✅ **獲取所有 `client_id`**
def get_clients_list():
    """🔍 讀取所有 `client_id`，用於遍歷查詢 """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT DISTINCT client_id FROM clients_file_mapping_table")
            clients = [row["client_id"] for row in cursor.fetchall()]
        
        logger.info(f"✅ 獲取 {len(clients)} 個客戶: {clients}")
        return clients
    except Exception as err:
        logger.error(f"❌ 無法讀取 `clients_file_mapping_table`，錯誤: {err}")
        return []
    finally:
        if connection:
            connection.close()  # ✅ 確保連線關閉

# ✅ **獲取特定客戶的數據存儲設置**
def get_client_data_settings(client_id):
    """📌 **獲取客戶的 `client_data_folder` 設置**"""
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT client_id, LOWER(storage_type) AS storage_type,
                       client_data_folder, client_file_prefix, 
                       client_file_primary_keys, updated_at
                FROM clients_file_mapping_table
                WHERE client_id = %s
            """
            cursor.execute(query, (client_id,))
            result = cursor.fetchall()

        if result:
            files_mapping = {}
            for r in result:
                prefix = r["client_file_prefix"]
                primary_keys_text = r["client_file_primary_keys"]

                if prefix:
                    primary_keys_list = primary_keys_text.split(",") if primary_keys_text else []
                    primary_keys_list = [col.strip() for col in primary_keys_list]
                    files_mapping[prefix] = primary_keys_list

            if not files_mapping:
                logger.warning(f"⚠️ `{client_id}` 沒有 `client_file_prefix`，請檢查數據庫！")
                return None

            client_data_folder = result[0].get("client_data_folder", "UNKNOWN_FOLDER")
            storage_type = result[0].get("storage_type", "UNKNOWN_STORAGE")

            mapping = {
                "client_data_folder": client_data_folder,
                "storage_type": storage_type,
                "files": files_mapping
            }

            logger.info(f"✅ `client_id={client_id}` 設置: {mapping}")
            return mapping

        logger.warning(f"⚠️ `{client_id}` 無數據映射！")
        return None

    except Exception as err:
        logger.error(f"❌ 查詢 `clients_file_mapping_table` 失敗 (client_id={client_id})，錯誤: {err}")
        return None

    finally:
        if connection:
            connection.close()

# ✅ **獲取所有客戶完整數據**
def fetch_all_clients_data():
    """📊 讀取 `clients_file_mapping_table`，並以 DataFrame 返回 """
    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT id, client_id, LOWER(storage_type) AS storage_type, client_data_folder, client_file_prefix, 
                   client_file_primary_keys, updated_at
            FROM clients_file_mapping_table
            ORDER BY id ASC
            """
            cursor.execute(query)
            results = cursor.fetchall()

        if results:
            df = pd.DataFrame(results)
            df.fillna('', inplace=True)  # ✅ 避免 None 值
            table = tabulate(df, headers="keys", tablefmt="grid", showindex=False)
            logger.info("\n📌 **Clients File Mapping Table Data:**\n" + table)
            return df
        else:
            logger.warning("⚠️ `clients_file_mapping_table` 內沒有數據")
            return pd.DataFrame()
    except Exception as err:
        logger.error(f"❌ 無法讀取 `clients_file_mapping_table`，錯誤: {err}")
        return pd.DataFrame()
    finally:
        if connection:
            connection.close()

# ✅ **更新 MySQL `client_file_primary_keys`**
def update_client_primary_keys(client_id, prefix, cleaned_keys):
    """🛠 **將清理後的 `client_file_primary_keys` 更新回 MySQL**"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
            UPDATE clients_file_mapping_table 
            SET client_file_primary_keys = %s, updated_at = NOW()
            WHERE client_id = %s AND client_file_prefix = %s
            """
            cursor.execute(query, (", ".join(cleaned_keys), client_id, prefix))
            connection.commit()
            logger.info(f"✅ `client_id={client_id}`, `{prefix}` 的 `client_file_primary_keys` 已更新: {cleaned_keys}")
    except Exception as err:
        logger.error(f"❌ 更新 `client_file_primary_keys` 失敗 (client_id={client_id}, prefix={prefix})，錯誤: {err}")
    finally:
        if connection:
            connection.close()



# ✅ **測試區塊**
if __name__ == "__main__":
    logger.info("🚀 測試 `client_file_mapping_config.py`")
    
    # ✅ **獲取所有客戶列表**
    clients = get_clients_list()
    
    if not clients:
        logger.warning("⚠️ 沒有客戶數據，請確認數據庫內容")
        exit(1)
    
    # ✅ **批量處理所有客戶**
    for client_id in clients:
        logger.info(f"🔄 **處理客戶: {client_id}**")
        client_data = get_client_data_settings(client_id)
        
        if client_data:
            logger.info(f"📂 客戶數據 ({client_id}): {json.dumps(client_data, indent=2, ensure_ascii=False)}")

            # ✅ **更新 `client_file_primary_keys` 回 MySQL**
            for prefix, keys in client_data["files"].items():
                update_client_primary_keys(client_id, prefix, keys)

    logger.info("✅ **所有客戶數據處理完成！**")