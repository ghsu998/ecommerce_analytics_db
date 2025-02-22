import requests
import pandas as pd
import mysql.connector
from io import BytesIO

# 🟢 設定 OneDrive API 認證資訊
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"
file_id = "015W3F6FRPZ7MVOCGDUBGZCO57TH2VGVV6"  # Kinger_Ecommerce_Analysis.xlsx 的 ID
table_name = "container_log"  # MySQL Table 名稱
sheet_name = "Container Log"  # Excel Sheet 名稱（非 Table）

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
        return BytesIO(response.content)
    else:
        print(f"❌ 下載失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")
        return None

# 🟢 讀取 Excel Sheet
def read_excel_sheet(excel_file, sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl", header=0)  # 指定 header=0

    # 🟢 修正欄位名稱，確保不會有數值型欄位名稱
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]

    print(f"✅ 成功讀取 `{sheet_name}` 的 Table，列數: {len(df.columns)}")
    print(f"🟢 修正後的欄位名稱: {df.columns.tolist()}")

    return df

# 🟢 連接 MySQL
def connect_mysql():
    return mysql.connector.connect(
        host="173.201.189.56",
        port=3306,
        user="gary",
        password="gaga5288#5288#5288",
        database="ecommerce_analytics_db"
    )

# 🟢 建立/更新 MySQL Table Schema
def update_table_schema(df, connection, table_name):
    cursor = connection.cursor()

    # 取得當前 Table Schema
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print(f"⚠️ `{table_name}` 不存在，創建新 Table...")
    else:
        print(f"✅ `{table_name}` 已存在，準備更新 Schema...")

    # 創建新的 Table
    column_definitions = ", ".join([f"`{col}` TEXT" for col in df.columns])
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

    # 🟢 清理 NaN，轉換為 None
    df = df.where(pd.notna(df), None)  # Pandas NaN -> Python None
    df = df.replace({pd.NA: None, "nan": None, "NaN": None, "": None, float("nan"): None})  # 進一步清理 nan

    # 🟢 確保所有欄位都是 `str`，避免數字當成列名
    df.columns = df.columns.astype(str)

    # 🟢 動態生成 SQL INSERT 語句
    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

    data_tuples = [tuple(row) for row in df.to_numpy()]

    # **完全覆蓋 Table**
    cursor.execute(f"DELETE FROM `{table_name}`")
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

    # 讀取 Excel Sheet
    df = read_excel_sheet(excel_file, sheet_name)

    # 連接 MySQL 並更新 Schema
    connection = connect_mysql()
    update_table_schema(df, connection, table_name)
    
    # 插入數據
    insert_data_to_mysql(df, connection, table_name)

    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()