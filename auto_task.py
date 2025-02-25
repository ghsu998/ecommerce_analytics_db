import subprocess
import time
import pymysql
import logging
from tqdm import tqdm  # 進度條

# 🟢 設定 MySQL 連線資訊
MYSQL_CONFIG = {
    "host": "173.201.189.56",
    "port": 3306,
    "user": "gary",
    "password": "gaga5288#5288#5288",
    "database": "ecommerce_analytics_db"
}

# 🟢 設定日誌紀錄
LOG_FILE = "auto_task_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🟢 定義要執行的同步腳本 (Python & SQL)
SYNC_TASKS = [
    # 4Seller 訂單數據處理
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/order_4seller_raw_upload.py", "訂單數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/order_4seller_clean.sql", "訂單數據清理", "sql"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/order_4seller_clean_download.py", "訂單數據下載", "python"),

    # OneDrive 數據同步
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_container_log.py", "Container Log 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_data_payouts.py", "Data_Payouts 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_data_sales_clean.py", "Data_Sales_Clean 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_data_salespayouts_clean.py", "Data_Sales_Payouts_Clean 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_data_sales_raw.py", "Data_Sales 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_data_weekly_sold_clean.py", "Data_Weekly_Sold_Clean 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_sync_sku_analysis.py", "SKU_Analysis 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_update_data_inventory_clean.py", "Data_Inventory_Clean 數據上傳", "python"),
    ("/Users/gary/Documents/GitHub/ecommerce_analytics_db/onedrive_update_data_weekly_sales_raw.py", "data_weekly_sales_raw 數據上傳", "python"),

]

# 🟢 執行 Python 腳本
def execute_python_script(script_path, description):
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        logging.info(f"✅ {description} 成功！")
        print(result.stdout)
        if result.stderr:
            logging.warning(f"⚠️ {description} 錯誤: {result.stderr}")
            print(f"⚠️ 錯誤訊息: {result.stderr}")
    except Exception as e:
        logging.error(f"❌ 執行 {description} 時發生錯誤: {e}")
        print(f"❌ 執行 {description} 時發生錯誤: {e}")

# 🟢 執行 SQL 腳本
def execute_sql_script(sql_path, description):
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        with open(sql_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()

        # 逐條執行 SQL 指令
        for sql in sql_commands.split(';'):
            sql = sql.strip()
            if sql:
                try:
                    cursor.execute(sql)
                except Exception as sql_error:
                    logging.error(f"❌ SQL 執行錯誤: {sql}，錯誤訊息: {sql_error}")

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"✅ {description} SQL 執行成功！")
        print(f"✅ {description} SQL 執行成功！")

    except Exception as e:
        logging.error(f"❌ {description} SQL 執行失敗: {e}")
        print(f"❌ {description} SQL 執行失敗: {e}")

# 🟢 執行所有同步腳本（進度條 + 間隔）
print("🚀 開始執行同步任務...")
logging.info("🚀 開始執行同步任務...")

with tqdm(total=len(SYNC_TASKS), desc="同步進度", unit="task") as pbar:
    for script in SYNC_TASKS:
        script_path = script[0]
        description = script[1]
        script_type = script[2]

        print(f"\n🔹 執行: {description} ({script_path})...")
        logging.info(f"🔹 開始執行: {description} ({script_path})...")

        if script_type == "python":
            execute_python_script(script_path, description)
        elif script_type == "sql":
            execute_sql_script(script_path, description)

        # 更新進度條
        pbar.update(1)

        # **避免影響 MySQL 運行，每個任務間隔 5 秒**
        time.sleep(5)

print("\n🎯 所有同步任務完成！")
logging.info("🎯 所有同步任務完成！")