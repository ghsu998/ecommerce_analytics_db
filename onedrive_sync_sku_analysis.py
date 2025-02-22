import requests
import pandas as pd
import mysql.connector
from io import BytesIO

# 🟢 設定 OneDrive API 認證資訊
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"
file_id = "015W3F6FRPZ7MVOCGDUBGZCO57TH2VGVV6"  # Kinger_Ecommerce_Analysis.xlsx 的 ID
sheet_name = "SKU_Analysis"

# 🟢 取得 Access Token
def get_access_token():
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
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
    file_url = f"https://graph.microsoft.com/v1.0/users/gary@kingerinc.com/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(file_url, headers=headers)

    if response.status_code == 200:
        print("✅ 成功下載 Excel 檔案！")
        return BytesIO(response.content)  # 轉為 BytesIO 物件
    else:
        print(f"❌ 下載失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")
        return None

# 🟢 連接 MySQL
def connect_mysql():
    return mysql.connector.connect(
        host="173.201.189.56",
        port=3306,
        user="gary",
        password="gaga5288#5288#5288",
        database="ecommerce_analytics_db"
    )

# 🟢 清理欄位名稱 (去空格並轉為 `_`)
def clean_column_names(columns):
    return [col.strip().replace(" ", "_") for col in columns]

# 🟢 更新 MySQL Table 結構 (修正 cursor.connection.commit() 問題)
def update_table_schema(df, connection, table_name):
    cursor = connection.cursor()

    # 取得當前表結構
    cursor.execute(f"DESCRIBE `{table_name}`")
    existing_columns = {row[0] for row in cursor.fetchall()}

    # 檢查是否有新的欄位
    for col in df.columns:
        if col not in existing_columns:
            print(f"🟡 新增欄位: {col}")
            alter_query = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` VARCHAR(255);"
            cursor.execute(alter_query)

    # **修正 cursor.connection.commit() 問題**
    connection.commit()
    cursor.close()

# 🟢 建立 MySQL Table
def create_table_if_not_exists(df, connection, table_name):
    cursor = connection.cursor()

    # 生成 CREATE TABLE 語句
    column_definitions = ", ".join([f"`{col}` VARCHAR(255)" for col in df.columns])
    create_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        {column_definitions}
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_query)
    connection.commit()
    cursor.close()
    print(f"✅ `{table_name}` 已創建！")

# 🟢 插入數據到 MySQL (修正 NaN 問題)
def insert_data_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    # **1️⃣ 轉換所有 NaN 為 None**
    df = df.where(pd.notna(df), None)

    # **2️⃣ 確保數據類型一致，避免 MySQL 錯誤**
    df = df.astype(str).replace({"nan": None, "NaN": None, "None": None, "": None})

    # **3️⃣ 生成 INSERT 語句**
    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

    # **4️⃣ 轉換 DataFrame 為 list of tuples**
    data_tuples = [tuple(row) for row in df.to_numpy()]

    # **5️⃣ 插入數據**
    cursor.executemany(insert_query, data_tuples)
    connection.commit()
    cursor.close()
    print(f"✅ {cursor.rowcount} 筆數據已插入 `{table_name}`！")
    
# 🟢 主執行流程
def main():
    access_token = get_access_token()
    if not access_token:
        print("❌ 無法獲取 Access Token")
        return

    excel_file = download_excel_from_onedrive(access_token, file_id)
    if not excel_file:
        return

    # 讀取指定 Sheet
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')

    # 清理欄位名稱
    df.columns = clean_column_names(df.columns)

    # 連接 MySQL
    connection = connect_mysql()

    table_name = "sku_analysis"

    # 檢查 Table 是否存在
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    cursor.close()

    if not table_exists:
        print(f"⚠️ `{table_name}` 不存在，創建新 Table！")
        create_table_if_not_exists(df, connection, table_name)
    else:
        print(f"✅ `{table_name}` 存在，檢查是否需要更新欄位...")
        update_table_schema(df, connection, table_name)

    # 清空表格，避免數據重複
    cursor = connection.cursor()
    cursor.execute(f"TRUNCATE TABLE `{table_name}`")
    connection.commit()
    cursor.close()
    print(f"🗑 `{table_name}` 已清空，準備插入新數據！")

    # 插入數據
    insert_data_to_mysql(df, connection, table_name)

    # 關閉 MySQL 連線
    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()