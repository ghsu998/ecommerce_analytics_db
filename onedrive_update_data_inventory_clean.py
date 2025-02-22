import requests
import pandas as pd
import mysql.connector
from io import BytesIO

# 🟢 設定 OneDrive API 認證資訊
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"
file_id = "015W3F6FRPZ7MVOCGDUBGZCO57TH2VGVV6"
sheet_name = "Data_Inventory_Clean"

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

# 🟢 讀取 Excel Sheet
def read_excel_sheet(excel_file, sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl", header=None)

    for i, row in df.iterrows():
        if all(isinstance(cell, str) for cell in row):  
            header_row = i
            print(f"✅ 找到表頭行：第 {header_row + 1} 行")
            break
    else:
        print("❌ 無法找到表頭，請檢查 Excel 文件！")
        exit()

    df.columns = df.iloc[header_row]
    df = df[(header_row + 1):].reset_index(drop=True)
    
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

# 🟢 更新 MySQL Table 結構
def update_table_schema(df, connection, table_name):
    cursor = connection.cursor()

    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    existing_columns = {row[0] for row in cursor.fetchall()}

    excel_columns = set(df.columns)
    columns_to_add = excel_columns - existing_columns 

    for col in columns_to_add:
        print(f"🟡 新增欄位: {col}")
        cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` VARCHAR(255)")

    connection.commit()
    cursor.close()
    print(f"✅ `{table_name}` Schema 已同步！")

# 🟢 建立 MySQL Table（修正 PRIMARY KEY 問題）
def create_table_if_not_exists(df, connection, table_name):
    cursor = connection.cursor()

    df_columns = df.columns.tolist()
    df_columns.remove("InventoryDate")  # **避免重複定義**
    df_columns.remove("SKU_Warehouse_Key")  # **避免重複定義**
    
    column_definitions = ", ".join([f"`{col}` VARCHAR(255)" for col in df_columns])
    create_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        InventoryDate DATE NOT NULL,
        SKU_Warehouse_Key VARCHAR(255) NOT NULL,
        {column_definitions},
        PRIMARY KEY (InventoryDate, SKU_Warehouse_Key)
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_query)
    connection.commit()
    cursor.close()
    print(f"✅ `{table_name}` 已創建，並設定 PRIMARY KEY (InventoryDate, SKU_Warehouse_Key)！")

# 🟢 插入或更新數據到 MySQL
def insert_or_update_data_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    df = df.where(pd.notna(df), None)
    df = df.astype(str).replace({"nan": None, "NaN": None, "None": None, "": None})

    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    update_clause = ", ".join([f"`{col}`=VALUES(`{col}`)" for col in df.columns if col not in ["InventoryDate", "SKU_Warehouse_Key"]])

    insert_query = f"""
    INSERT INTO `{table_name}` ({columns})
    VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE {update_clause};
    """

    data_tuples = [tuple(row) for row in df.to_numpy()]
    cursor.executemany(insert_query, data_tuples)
    connection.commit()
    print(f"✅ {cursor.rowcount} 筆數據已同步 `{table_name}`！")

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
    table_name = sheet_name.lower().replace(" ", "_")

    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    cursor.close()

    if not table_exists:
        create_table_if_not_exists(df, connection, table_name)
    else:
        update_table_schema(df, connection, table_name)

    insert_or_update_data_to_mysql(df, connection, table_name)
    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()