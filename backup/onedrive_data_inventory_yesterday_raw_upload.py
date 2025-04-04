import json
import requests
import pandas as pd
import pymysql
from io import BytesIO
import re
import os
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

# 🟢 OneDrive API 設定
client_id = one_drive_config.get("client_id")
client_secret = one_drive_config.get("client_secret")
tenant_id = one_drive_config.get("tenant_id")
folder_id = one_drive_config.get("inventory_folder_id")  # ✅ 動態讀取
main_file_id = one_drive_config.get("inventory_main_file_id")

# 🟢 **固定的 Sheet 名稱**
main_sheet_name = "Inventory_Yesterday_History"
daily_sheet_name = "Sheet1"

# 🟢 **取得 Access Token**
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

# 🟢 取得最新的 `Data_Inventory_Yesterday_YYYY_MM_DD.xlsx`
def get_latest_inventory_file(access_token, folder_id):
    user_email = one_drive_config.get("user_email")
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ 無法獲取 `data` 資料夾內的文件資訊，API 回應: {response.text}")
        return None, None

    files = response.json().get("value", [])
    pattern = re.compile(r"Data_Inventory_Yesterday_(\d{4}_\d{2}_\d{2})\.xlsx")
    inventory_files = [(datetime.strptime(m.group(1), "%Y_%m_%d"), f["id"], m.group(1))
                       for f in files if (m := pattern.match(f["name"]))]

    if not inventory_files:
        print("❌ 未找到符合條件的最新檔案")
        return None, None

    latest_file = max(inventory_files, key=lambda x: x[0])
    print(f"✅ 最新庫存檔案: {latest_file}")
    return latest_file[1], latest_file[2]

# 🟢 下載 OneDrive Excel 檔案
def download_excel_from_onedrive(access_token, file_id):
    user_email = one_drive_config.get("user_email")
    file_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(file_url, headers=headers)
    return BytesIO(response.content) if response.status_code == 200 else None

# 🟢 **上傳 OneDrive Excel 檔案**
def upload_to_onedrive(access_token, file_id, df):
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=main_sheet_name)
    excel_buffer.seek(0)

    user_email = one_drive_config.get("user_email")
    upload_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    response = requests.put(upload_url, headers=headers, data=excel_buffer)
    if response.status_code in [200, 201]:
        print("✅ 成功上傳合併後的檔案到 OneDrive！")
    else:
        print(f"❌ 上傳失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")

# 🟢 **讀取並清理 Excel**
def read_and_clean_excel(excel_file, sheet_name):
    xls = pd.ExcelFile(excel_file, engine="openpyxl")

    if sheet_name not in xls.sheet_names:
        raise ValueError(f"❌ Excel 檔案內沒有 `{sheet_name}`，請檢查 Sheet 名稱！")

    df = pd.read_excel(xls, sheet_name=sheet_name, index_col=None)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
    df.columns = [re.sub(r"[^\w\s]", "", str(col)).strip().replace(" ", "_") for col in df.columns]

    if "Warehouse" in df.columns:
        df = df[df["Warehouse"].notna() & (df["Warehouse"].astype(str).str.strip() != "")]

    if "InventoryDate" in df.columns:
        df["InventoryDate"] = pd.to_datetime(df["InventoryDate"], errors="coerce").dt.strftime('%Y-%m-%d')

    if "Last_Received" in df.columns:
        df["Last_Received"] = pd.to_datetime(df["Last_Received"], errors="coerce").dt.strftime('%Y-%m-%d')
        df["Last_Received"] = df["Last_Received"].where(pd.notna(df["Last_Received"]), None)

    df = df.astype(str).replace(["nan", "NaN", "None", "NULL", ""], None)
    df = df.where(pd.notna(df), None)

    print(f"✅ 清理後數據量: {len(df)} 行")
    return df

# 🟢 **連接 MySQL**
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

# 🟢 **上傳 MySQL**
def upload_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))

    insert_query = f"""
        INSERT INTO `{table_name}` ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {", ".join([f"`{col}`=VALUES(`{col}`)" for col in df.columns])};
    """

    data_tuples = [tuple(row) for row in df.to_numpy()]
    cursor.executemany(insert_query, data_tuples)
    connection.commit()
    print(f"✅ {cursor.rowcount} 筆數據已同步 `{table_name}`！")
    cursor.close()

# 🟢 **主執行流程**
def main():
    table_name = "data_inventory_yesterday_raw"

    access_token = get_access_token()
    if not access_token:
        print("❌ 無法獲取 Access Token")
        return

    latest_file_id, inventory_date = get_latest_inventory_file(access_token, folder_id)
    if not latest_file_id:
        return

    df_new = read_and_clean_excel(download_excel_from_onedrive(access_token, latest_file_id), daily_sheet_name)
    df_main = read_and_clean_excel(download_excel_from_onedrive(access_token, main_file_id), main_sheet_name)
    
    df_merged = pd.concat([df_main, df_new], ignore_index=True).drop_duplicates(subset=["SKU", "InventoryDate", "Warehouse"])
    upload_to_onedrive(access_token, main_file_id, df_merged)
    
    connection = connect_mysql()
    upload_to_mysql(df_merged, connection, table_name)
    connection.close()

if __name__ == "__main__":
    main()