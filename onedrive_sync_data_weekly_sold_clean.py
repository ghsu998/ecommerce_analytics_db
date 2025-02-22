import requests
import pandas as pd
import mysql.connector
from io import BytesIO

# 🟢 設定 OneDrive API 認證資訊
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"
file_id = "015W3F6FRPZ7MVOCGDUBGZCO57TH2VGVV6"  # OneDrive 檔案 ID
sheet_name = "Data_Weekly_Sold_Clean"  # 需要同步的 Excel Sheet 名稱

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

# 🟢 讀取 Excel Sheet（自動找標題行）
def read_excel_sheet(excel_file, sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl", header=None)

    # 🟢 自動尋找正確的表頭行
    for i, row in df.iterrows():
        if all(isinstance(cell, str) for cell in row):  # 確保整列為 **字串**
            header_row = i
            print(f"✅ 找到表頭行：第 {header_row + 1} 行")
            break
    else:
        print("❌ 無法找到表頭，請檢查 Excel 文件！")
        exit()

    # 🟢 設定找到的行作為標題
    df.columns = df.iloc[header_row]
    df = df[(header_row + 1):].reset_index(drop=True)

    # 🟢 修正欄位名稱（去除空格，轉換數字欄位名稱）
    df.columns = [str(col).strip().replace(" ", "_") if isinstance(col, str) else f"Column_{i}" for i, col in enumerate(df.columns)]

    print(f"✅ `{sheet_name}` 讀取成功，處理後欄位名稱: {df.columns.tolist()}")
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

# 🟢 更新 MySQL Table 結構（新增/刪除 欄位）
def update_table_schema(df, connection, table_name):
    cursor = connection.cursor()

    # 取得現有的欄位
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    existing_columns = {row[0] for row in cursor.fetchall()}

    # **找出需要刪除的欄位**
    excel_columns = set(df.columns)
    columns_to_remove = existing_columns - excel_columns  # MySQL 有，但 Excel 沒有的欄位

    # **找出需要新增的欄位**
    columns_to_add = excel_columns - existing_columns  # Excel 有，但 MySQL 沒有的欄位

    # **刪除 Excel 內已不存在的欄位**
    for col in columns_to_remove:
        print(f"🗑 移除舊欄位: {col}")
        cursor.execute(f"ALTER TABLE `{table_name}` DROP COLUMN `{col}`")

    # **新增缺少的欄位**
    for col in columns_to_add:
        print(f"🟡 新增欄位: {col}")
        cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` VARCHAR(255)")

    connection.commit()
    cursor.close()
    print(f"✅ `{table_name}` Schema 已與 Excel Sheet 完全同步！")

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

# 🟢 插入數據到 MySQL（清空後重新插入）
def insert_data_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    # **轉換所有 NaN 為 None**
    df = df.where(pd.notna(df), None)

    # **確保數據類型一致**
    df = df.astype(str).replace({"nan": None, "NaN": None, "None": None, "": None})

    # **生成 INSERT 語句**
    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

    # **轉換 DataFrame 為 list of tuples**
    data_tuples = [tuple(row) for row in df.to_numpy()]

    # **清空表格**
    cursor.execute(f"TRUNCATE TABLE `{table_name}`")
    connection.commit()

    # **插入數據**
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

    # 讀取 Excel Sheet
    df = read_excel_sheet(excel_file, sheet_name)

    # 連接 MySQL
    connection = connect_mysql()

    # 設定 MySQL Table 名稱（根據 sheet_name 轉小寫）
    table_name = sheet_name.lower().replace(" ", "_")

    # **檢查 Table 是否存在**
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    cursor.close()

    if not table_exists:
        create_table_if_not_exists(df, connection, table_name)
    else:
        update_table_schema(df, connection, table_name)

    # **插入數據**
    insert_data_to_mysql(df, connection, table_name)

    # 關閉 MySQL 連線
    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()