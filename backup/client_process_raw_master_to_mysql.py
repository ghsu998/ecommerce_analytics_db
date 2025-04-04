import os
import pandas as pd
from api_mysql_functions import get_all_tables, insert_or_update_data, get_client_file_mapping_data, get_all_client_ids
from api_mysql import get_db_connection
from app_config import get_config_value, logger
from app_utility import clean_column_names, format_date_columns

def create_client_raw_master_table():
    """🔧 確保 `client_raw_master_data` 表格存在"""
    table_name = "client_raw_master_data"
    connection = get_db_connection()
    if not connection:
        logger.error("❌ 無法建立 MySQL 連線，無法檢查/創建表格")
        return
    
    try:
        with connection.cursor() as cursor:
            if table_name not in get_all_tables():
                create_table_query = f'''
                CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id VARCHAR(50),
                    client_file_prefix_master VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
                '''
                cursor.execute(create_table_query)
                connection.commit()
                logger.info(f"✅ 表格 {table_name} 創建成功！")
            else:
                logger.info(f"✅ 表格 {table_name} 已存在，無需創建")
    except Exception as e:
        logger.error(f"❌ 創建表格 {table_name} 失敗: {e}")
    finally:
        connection.close()

def process_and_upload_master_data(client_id):
    """📤 解析 `raw_master.xlsx` 並上傳到 MySQL"""
    client_data = get_client_file_mapping_data(client_id)
    if not client_data:
        logger.warning(f"⚠️ 找不到 `{client_id}` 的檔案映射配置，跳過！")
        return
    
    for mapping in client_data:
        storage_type = mapping['storage_type']
        client_file_prefix = mapping['client_file_prefix']
        master_filename = f"{client_file_prefix}_master.xlsx"
        file_path = os.path.join("data", master_filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ 檔案 {file_path} 不存在，跳過 `{client_id}`")
            continue
        
        df = pd.read_excel(file_path)
        df = clean_column_names(df)
        df = format_date_columns(df)
        
        df.insert(0, "client_id", client_id)
        df.insert(1, "client_file_prefix_master", client_file_prefix)
        
        table_name = "client_raw_master_data"
        columns = df.columns.tolist()
        data_rows = df.values.tolist()
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table_name} WHERE client_id = %s", (client_id,))
                connection.commit()
                logger.info(f"🗑️ 已清空 `{client_id}` 的舊數據")
        except Exception as e:
            logger.error(f"❌ 無法清空 `{client_id}` 的數據: {e}")
        finally:
            connection.close()
        
        insert_or_update_data(table_name, columns, data_rows, columns)
        logger.info(f"✅ `{client_id}` 數據已成功更新到 MySQL！")

if __name__ == "__main__":
    logger.info("🚀 開始處理所有客戶的 `raw_master.xlsx` 數據並上傳到 MySQL...")
    create_client_raw_master_table()
    client_ids = get_all_client_ids()
    for client_id in client_ids:
        process_and_upload_master_data(client_id)
    logger.info("🎯 所有客戶數據處理完成！")
