import requests
import pandas as pd
import mysql.connector
from io import BytesIO
import re
from datetime import datetime

# 🟢 OneDrive API 設定
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"
folder_id = "015W3F6FX44DSBW2E25RAYHT7ZHOC6EOOU"  # 📂 `data` 資料夾的 ID
main_file_id = "015W3F6FRGKNZC4KGGSFEZ7AKX4IXT2652"  # 📄 `Data_Weekly_Sold.xlsx` 固定 ID

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
    return response.json().get("access_token", None)

# 🟢 取得最新的週報檔案 ID
def get_latest_file_id(access_token, folder_id):
    user_email = "gary@kingerinc.com"
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ 無法獲取 `data` 資料夾內的文件資訊，API 回應: {response.text}")
        return None, None, None

    files = response.json().get("value", [])
    pattern = re.compile(r"Data_Weekly_Sold_(\d{4}_\d{2}_\d{2})_(\d{4}_\d{2}_\d{2})\.xlsx")
    weekly_files = [(datetime.strptime(m.groups()[0], "%Y_%m_%d"), f["id"], *m.groups()) 
                    for f in files if (m := pattern.match(f["name"]))]

    if not weekly_files:
        print("❌ 未找到符合條件的最新檔案")
        return None, None, None

    latest_file = max(weekly_files, key=lambda x: x[0])
    print(f"✅ 最新檔案: {latest_file}")
    return latest_file[1], latest_file[2], latest_file[3]

# 🟢 下載 OneDrive Excel 檔案
def download_excel_from_onedrive(access_token, file_id):
    user_email = "gary@kingerinc.com"
    file_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(file_url, headers=headers)
    return BytesIO(response.content) if response.status_code == 200 else None

# 🟢 讀取 Excel 第一個 Sheet
def read_excel_sheet(excel_file):
    xls = pd.ExcelFile(excel_file, engine="openpyxl")
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]
    return df

# 🟢 合併數據，避免重複
def merge_dataframes(df_main, df_new, start_date, end_date):
    df_new["Start_Date"] = start_date
    df_new["End_Date"] = end_date
    df_merged = pd.concat([df_main, df_new], ignore_index=True).drop_duplicates(subset=["SKU", "Start_Date", "End_Date"])
    return df_merged

# 🟢 上傳合併後的 Excel 回 OneDrive
def upload_to_onedrive(access_token, file_id, df):
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Weekly_Sales")
    excel_buffer.seek(0)

    user_email = "gary@kingerinc.com"
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

# 🟢 連接 MySQL
def connect_mysql():
    return mysql.connector.connect(
        host="173.201.189.56",
        port=3306,
        user="gary",
        password="gaga5288#5288#5288",
        database="ecommerce_analytics_db"
    )

# 🟢 上傳數據到 MySQL（如果已存在則更新）
def upload_to_mysql(df, connection, table_name):
    cursor = connection.cursor()

    # 🚀 準備 INSERT ... ON DUPLICATE KEY UPDATE 查詢
    columns = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    update_clause = ", ".join([f"`{col}`=VALUES(`{col}`)" for col in df.columns if col not in ["SKU", "End_Date"]])

    insert_query = f"""
        INSERT INTO `{table_name}` ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause};
    """

    # 🚀 清理數據（去掉 NaN）
    df = df.where(pd.notna(df), None)

    # 🚀 轉換 DataFrame 為 tuple 列表
    data_tuples = [tuple(row) for row in df.to_numpy()]

    # 🚀 批量執行
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
    
    latest_file_id, start_date, end_date = get_latest_file_id(access_token, folder_id)
    if not latest_file_id:
        print("⚠️ 未找到最新的 `Data_Weekly_Sold_YYYY_MM_DD_YYYY_MM_DD.xlsx`，請確認 OneDrive 檔案")
        return
    
    main_file = download_excel_from_onedrive(access_token, main_file_id)
    new_file = download_excel_from_onedrive(access_token, latest_file_id)
    if not main_file or not new_file:
        print("❌ 下載失敗")
        return
    
    df_main = read_excel_sheet(main_file)  # 🚀 讀取主檔案
    df_new = read_excel_sheet(new_file)  # 🚀 讀取最新週報檔案

    df_merged = merge_dataframes(df_main, df_new, start_date, end_date)

    # ✅ 上傳回 OneDrive，更新主檔案
    upload_to_onedrive(access_token, main_file_id, df_merged)

    # 🔹 MySQL 上傳（現在啟用）
    connection = connect_mysql()
    upload_to_mysql(df_merged, connection, "data_weekly_sales_raw")
    connection.close()

# 🚀 執行主流程
if __name__ == "__main__":
    main()