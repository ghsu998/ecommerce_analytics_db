import requests
import pandas as pd
import pymysql
import json
from io import BytesIO
import os

# 🟢 載入配置文件 (config.json)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

if not os.path.exists(CONFIG_PATH):
    print(f"❌ 找不到 `config.json`，請確認文件是否存在於 {CONFIG_PATH}")
    exit()

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

db_config = config.get("database", {}).get("mysql", {})
one_drive_config = config.get("storage", {}).get("onedrive", {})

# 🔹 設定檔案 & Sheet & Table
file_id = one_drive_config.get("kinger_ecommerce_analysis_xlsx_file_id")  # ✅ 讀取 OneDrive 檔案 ID
sheet_name = "Container_Log"  # ✅ 指定 Excel Sheet
table_name = "kin_sku_purchase_master"  # ✅ 指定 MySQL Table 名稱

# 🟢 欄位類型自動格式化
COLUMN_TYPES = {
    "Year": "Int64",
    "Month_Name": "string",
    "Date": "datetime64",
    "Marketplace": "string",
    "Category": "string",
    "Value": "float64",
    "Received_QTY": "Int64",
    "Landed_Cost": "float64",
    "CTN_PER_PLT": "Int64",
    "BOX_PER_CTN": "Int64",
    "PC_PER_CTN": "Int64"
}

def format_dataframe(df):
    """根據 `COLUMN_TYPES` 自動格式化 DataFrame"""
    for col, dtype in COLUMN_TYPES.items():
        if col in df.columns:
            if dtype == "Int64":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif dtype == "datetime64":
                df[col] = pd.to_datetime(df[col], errors="coerce")
            elif dtype == "float64":
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
            else:
                df[col] = df[col].astype(str).str.strip()
    return df

# 🟢 取得 Access Token
def get_access_token():
    token_url = f"https://login.microsoftonline.com/{one_drive_config.get('tenant_id')}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": one_drive_config.get("client_id"),
        "client_secret": one_drive_config.get("client_secret"),
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(token_url, data=token_data)
    token_json = response.json()

    if "access_token" in token_json:
        print("✅ Access Token 獲取成功！")
        return token_json["access_token"]
    else:
        print(f"❌ Access Token 獲取失敗，錯誤訊息：{token_json}")
        exit()

# 🟢 下載 OneDrive Excel
def download_excel_from_onedrive(access_token, file_id):
    file_url = f"https://graph.microsoft.com/v1.0/users/{one_drive_config.get('user_email')}/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(file_url, headers=headers)

    if response.status_code == 200:
        print("✅ 成功下載 Excel 檔案！")
        return BytesIO(response.content)
    else:
        print(f"❌ 下載失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")
        return None

# 🟢 讀取 Excel Sheet
def read_excel_sheet(excel_file, sheet_name):
    xls = pd.ExcelFile(excel_file, engine="openpyxl")
    print("📌 Excel 內的 Sheets:", xls.sheet_names)

    if sheet_name not in xls.sheet_names:
        print(f"❌ 找不到 Sheet: {sheet_name}")
        print("📌 可用的 Sheets:", xls.sheet_names)
        exit()

    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl", header=0)
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]
    df = format_dataframe(df)

    print(f"✅ 成功讀取 `{sheet_name}`，共 {df.shape[0]} 行, {df.shape[1]} 列")
    print(f"🛠 轉換後的欄位格式: {df.dtypes}")

    return df

# 🟢 連接 MySQL
def connect_mysql():
    try:
        connection = pymysql.connect(
            host=db_config.get("host"),
            port=int(db_config.get("port", 3306)),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ MySQL 連線成功！")
        return connection
    except pymysql.MySQLError as err:
        print(f"❌ MySQL 連線失敗: {err}")
        exit()

# 🟢 建立/更新 MySQL Table Schema
def update_table_schema(df, connection, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print(f"⚠️ `{table_name}` 不存在，創建新 Table...")
    else:
        print(f"✅ `{table_name}` 已存在，準備更新 Schema...")

    column_definitions = ", ".join([
        f"`{col}` {'DECIMAL(12,2)' if COLUMN_TYPES.get(col) == 'float64' else 'INT' if COLUMN_TYPES.get(col) == 'Int64' else 'TEXT'}"
        for col in df.columns
    ])
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        {column_definitions}
    );
    """
    cursor.execute(create_table_sql)
    connection.commit()
    print(f"✅ `{table_name}` Schema 已更新！")
    cursor.close()

# 🟢 插入數據到 MySQL
def insert_data_to_mysql(df, connection, table_name):
    cursor = connection.cursor()
    df = df.where(pd.notna(df), None)

    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

    data_tuples = [tuple(row) for row in df.to_numpy()]
    cursor.execute(f"DELETE FROM `{table_name}`")  # **完全覆蓋 Table**
    cursor.executemany(insert_query, data_tuples)

    connection.commit()
    print(f"✅ {cursor.rowcount} 筆數據插入 `{table_name}`！")
    cursor.close()

# 🟢 主執行流程
def main():
    access_token = get_access_token()
    if not access_token:
        print("❌ 無法獲取 Access Token")
        return

    excel_file = download_excel_from_onedrive(access_token, file_id)
    if not excel_file:
        return

    df = read_excel_sheet(excel_file, sheet_name)
    connection = connect_mysql()
    update_table_schema(df, connection, table_name)
    insert_data_to_mysql(df, connection, table_name)
    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()