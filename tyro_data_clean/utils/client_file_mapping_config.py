import logging
import pandas as pd
import pymysql
import json
from tabulate import tabulate

from app_config import get_config_value, logger  # ✅ 確保從 `app_config.py` 讀取配置
from tyro_data_clean.utils.app_utility import clean_column_names  # ✅ 清理欄位名稱
from tyro_data_clean.apis.api_mysql import get_db_connection  # ✅ MySQL 連線

# ✅ **獲取所有 `client_id`**
def get_clients_list():
    """🔍 讀取所有 `client_id`，用於遍歷查詢"""
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
            connection.close()

def get_client_data_settings(client_id):
    """📌 獲取客戶的 `client_data_folder` 設置（支援同 client 多 prefix 聚合）"""
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

        if not result:
            logger.warning(f"⚠️ `{client_id}` 無數據映射！")
            return None

        # ✅ 聚合同一 client_id + client_data_folder 的所有 prefix
        grouped_config = {}
        for row in result:
            folder = row["client_data_folder"]
            storage = row["storage_type"]
            prefix = row["client_file_prefix"]
            primary_keys_text = row["client_file_primary_keys"]

            # 🧠 將同一 client 的設定合併起來（以 folder 為主）
            key = (folder, storage)
            if key not in grouped_config:
                grouped_config[key] = {
                    "client_data_folder": folder,
                    "storage_type": storage,
                    "files": {}
                }

            if prefix:
                primary_keys_list = [col.strip() for col in primary_keys_text.split(",")]
                grouped_config[key]["files"][prefix] = primary_keys_list

        # 🚨 若有多個 folder？目前僅取第一個（實務上應該只有一組）
        final_config = list(grouped_config.values())[0]

        if not final_config["files"]:
            logger.warning(f"⚠️ `{client_id}` 沒有任何有效的 prefix 設定")
            return None

        logger.info(f"✅ `client_id={client_id}` 設置: {final_config}")
        return final_config

    except Exception as err:
        logger.error(f"❌ 查詢失敗 (client_id={client_id})，錯誤: {err}")
        return None

    finally:
        if connection:
            connection.close()


# ✅ **讀取完整 DataFrame**
def fetch_all_clients_data():
    """📊 讀取 clients_file_mapping_table 並轉為 DataFrame"""
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
            df.fillna('', inplace=True)
            table = tabulate(df, headers="keys", tablefmt="grid", showindex=False)
            logger.info("\n📌 **Clients File Mapping Table Data:**\n" + table)
            return df
        else:
            logger.warning("⚠️ 資料表內沒有數據")
            return pd.DataFrame()
    except Exception as err:
        logger.error(f"❌ 無法讀取資料表，錯誤: {err}")
        return pd.DataFrame()
    finally:
        if connection:
            connection.close()

# ✅ **更新 `client_file_primary_keys` 回 MySQL**
def update_client_primary_keys(client_id, prefix, cleaned_keys):
    """🛠 將清理後的欄位寫回 MySQL"""
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
            logger.info(f"✅ 已更新: client_id={client_id}, prefix={prefix}, keys={cleaned_keys}")
    except Exception as err:
        logger.error(f"❌ 更新失敗 (client_id={client_id}, prefix={prefix})，錯誤: {err}")
    finally:
        if connection:
            connection.close()
