# ecommerce_analytics_db/tyro_data_db/schema_initializer.py

from .db_connection import get_db_connection
from datetime import datetime

# 定義所有必要的資料表

table_definitions = {
    "client_master_raw_files": """
        CREATE TABLE IF NOT EXISTS client_master_raw_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(50),
            upload_batch_id VARCHAR(100),
            filename VARCHAR(255),
            file_type VARCHAR(50),
            raw_data_json LONGTEXT,
            row_count INT,
            uploaded_at DATETIME,
            source VARCHAR(100),
            processed BOOLEAN DEFAULT FALSE,
            notes TEXT
        )
    """,
    "sales_master_table": """
        CREATE TABLE IF NOT EXISTS sales_master_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(50),
            sku VARCHAR(100),
            order_date DATE,
            units_sold INT,
            sales_amount DECIMAL(10,2),
            platform VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "inventory_master_table": """
        CREATE TABLE IF NOT EXISTS inventory_master_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            client_id VARCHAR(50),
            sku VARCHAR(100),
            snapshot_date DATE,
            inventory_level INT,
            inbound_units INT,
            outbound_units INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
}

# Logs 寫入函式

def log_trigger(message: str, category: str = "DB_INIT"):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = """
            INSERT INTO api_trigger_log (trigger_time, trigger_source, trigger_type, trigger_message)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (
            datetime.now(),
            "tyro_data_db.schema_initializer",
            category,
            message
        ))
    conn.commit()
    conn.close()

def ensure_database_schema():
    conn = get_db_connection()
    if not conn:
        print("❌ 無法取得資料庫連線")
        log_trigger("❌ 連線失敗，無法建立資料表", category="DB_ERROR")
        return
    try:
        with conn.cursor() as cursor:
            for table_name, ddl in table_definitions.items():
                print(f"🛠 檢查/建立資料表: {table_name}")
                cursor.execute(ddl)
                log_trigger(f"✅ 確認/建立完成: {table_name}")
        conn.commit()
        print("✅ 所有必要的資料表已確認/建立完畢")
        log_trigger("✅ 所有表格初始化成功")
    finally:
        conn.close()