import json
import requests
import pandas as pd
import pymysql
from io import BytesIO
import os
import re
from datetime import datetime

# 🟢 **載入 config.json**
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

if not os.path.exists(CONFIG_PATH):
    print(f"❌ 找不到 `config.json`，請確認文件是否存在於 {CONFIG_PATH}")
    exit()

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)

mysql_config = config.get("database", {}).get("mysql", {})
one_drive_config = config.get("storage", {}).get("onedrive", {})

# 🔹 設定檔案 & Sheet & Table
folder_id = one_drive_config.get("server_clients_data_folder_id")
main_file_id = "015W3F6FRGKNZC4KGGSFEZ7AKX4IXT2652"
table_name = "data_weekly_sales_raw"
main_sheet_name = "Weekly_Sales_History"  # ✅ 主檔案的 Sheet
new_data_sheet_name = "Sheet1"  # ✅ 新數據的 Sheet

# 🟢 取得 Access Token
def get_access_token():
    token_url = f"https://login.microsoftonline.com/{one_drive_config['tenant_id']}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": one_drive_config["client_id"],
        "client_secret": one_drive_config["client_secret"],
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

# 🟢 取得最新的週報檔案 ID
def get_latest_file_id(access_token, folder_id):
    user_email = one_drive_config["user_email"]
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ API 取得資料夾失敗: {response.text}")
        return None, None, None

    files = response.json().get("value", [])
    pattern = re.compile(r"Data_Weekly_Sold_(\d{4}_\d{2}_\d{2})_(\d{4}_\d{2}_\d{2})\.xlsx")

    weekly_files = [
        (datetime.strptime(m.groups()[0], "%Y_%m_%d"), f["id"], 
         datetime.strptime(m.groups()[0], "%Y_%m_%d").strftime('%Y-%m-%d'),
         datetime.strptime(m.groups()[1], "%Y_%m_%d").strftime('%Y-%m-%d'))
        for f in files if (m := pattern.match(f["name"]))
    ]

    if not weekly_files:
        print("❌ 未找到符合條件的最新檔案")
        return None, None, None

    latest_file = max(weekly_files, key=lambda x: x[0])
    print(f"✅ 最新檔案: {latest_file}")
    return latest_file[1], latest_file[2], latest_file[3]

# 🟢 下載 OneDrive Excel 檔案
def download_excel_from_onedrive(access_token, file_id):
    user_email = one_drive_config["user_email"]
    file_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(file_url, headers=headers)
    return BytesIO(response.content) if response.status_code == 200 else None

# 🟢 讀取並清理 Excel
def read_and_clean_excel(excel_file, sheet_name):
    xls = pd.ExcelFile(excel_file, engine="openpyxl")

    if sheet_name not in xls.sheet_names:
        raise ValueError(f"❌ 錯誤: Excel 檔案內沒有 `{sheet_name}`，請檢查 Sheet 名稱！")

    df = pd.read_excel(xls, sheet_name=sheet_name)

    # ✅ **清理欄位名稱**
    df.columns = [re.sub(r"[^\w\s]", "", str(col)).strip().replace(" ", "_") for col in df.columns]

    # ✅ **清理 NaN**
    df = df.astype(str)
    df.replace(["nan", "NaN", "None", "NULL", ""], None, inplace=True)
    df = df.where(pd.notna(df), None)

    print(f"✅ 清理後數據量: {len(df)} 行")
    return df

# 🟢 連接 MySQL
def connect_mysql():
    try:
        connection = pymysql.connect(
            host=mysql_config.get("host"),
            port=int(mysql_config.get("port", 3306)),
            user=mysql_config.get("user"),
            password=mysql_config.get("password"),
            database=mysql_config.get("database"),
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ MySQL 連線成功！")
        return connection
    except pymysql.MySQLError as err:
        print(f"❌ MySQL 連線失敗: {err}")
        exit()

# 🟢 上傳 MySQL 並計算 `新增/更新/重複`
def upload_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    update_clause = ", ".join([f"`{col}`=VALUES(`{col}`)" for col in df.columns if col not in ["SKU", "End_Date"]])

    insert_query = f"""
        INSERT INTO `{table_name}` ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause};
    """

    df = df.astype(str)
    df.replace(["nan", "NaN", "None", "NULL"], None, inplace=True)
    df = df.where(pd.notna(df), None)

    data_tuples = [tuple(row) for row in df.to_numpy()]
    
    try:
        cursor.executemany(insert_query, data_tuples)
        connection.commit()
        print(f"✅ {cursor.rowcount} 筆數據已同步 `{table_name}`！")
    except pymysql.MySQLError as err:
        print(f"❌ MySQL 錯誤: {err}")
    finally:
        cursor.close()

# 🟢 **主執行流程**
def main():
    access_token = get_access_token()
    if not access_token:
        print("❌ 無法獲取 Access Token")
        return

    latest_file_id, start_date, end_date = get_latest_file_id(access_token, folder_id)
    if not latest_file_id:
        return

    df_main = read_and_clean_excel(download_excel_from_onedrive(access_token, main_file_id), main_sheet_name)
    df_new = read_and_clean_excel(download_excel_from_onedrive(access_token, latest_file_id), new_data_sheet_name)

    df_new["Start_Date"] = start_date
    df_new["End_Date"] = end_date

    print(f"✅ 讀取主檔案數據: {len(df_main)} 行")
    print(f"✅ 讀取新數據: {len(df_new)} 行")

    df_merged = pd.concat([df_main, df_new], ignore_index=True).drop_duplicates(subset=["SKU", "Start_Date", "End_Date"])

    print(f"✅ 合併後總數據量: {len(df_merged)} 行")

    connection = connect_mysql()
    upload_to_mysql(df_merged, connection, table_name)
    connection.close()

if __name__ == "__main__":
    main()