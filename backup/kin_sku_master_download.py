import requests
import pandas as pd
import pymysql
import json
from io import BytesIO
import os

# 🟢 載入配置文件 (config.json)
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

db_config = config["database"].get("mysql", {})
one_drive_config = config.get("authentication", {}).get("microsoftcloud", {})

# 🔹 設定檔案 & Sheet & Table
file_id = one_drive_config.get("kinger_ecommerce_analysis_xlsx_file_id")  # ✅ 讀取 OneDrive 檔案 ID
sheet_name = "SKU_Analysis"  # ✅ 指定 Excel Sheet
table_name = "kin_sku_master"  # ✅ 指定 MySQL Table 名稱

# 🟢 欄位類型自動格式化
COLUMN_TYPES = {
    "Year": "Int64",
    "Month_Name": "string",
    "Date": "datetime64",
    "Marketplace": "string",
    "Category": "string",
    "Value": "float64",  # 會自動轉換成 Decimal(12,2)
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
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)  # 保留 2 位小數
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

# 🟢 連接 MySQL
def connect_mysql():
    return pymysql.connect(
        host=db_config.get("host"),
        port=int(db_config.get("port", 3306)),
        user=db_config.get("user"),
        password=db_config.get("password"),
        database=db_config.get("database"),
        cursorclass=pymysql.cursors.DictCursor
    )

# 🟢 主執行流程
def main():
    access_token = get_access_token()
    if not access_token:
        print("❌ 無法獲取 Access Token")
        return

    excel_file = download_excel_from_onedrive(access_token, file_id)
    if not excel_file:
        return

    df = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl", header=0)
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]
    df = format_dataframe(df)

    connection = connect_mysql()
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM `{table_name}`")
    insert_query = f"INSERT INTO `{table_name}` ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))})"
    cursor.executemany(insert_query, [tuple(row) for row in df.to_numpy()])
    connection.commit()
    cursor.close()
    connection.close()
    print(f"✅ {len(df)} 筆數據插入 `{table_name}`！")

# 🚀 執行主流程
if __name__ == "__main__":
    main()