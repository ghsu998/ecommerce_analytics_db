import requests

# 🟢 設定 Microsoft Graph API 認證資訊
client_id = "48643d80-3543-400c-8e63-8c7b76377ab6"
client_secret = "IoD8Q~uHu~SAISKLUZx0BcVs2xdrsd2fWXjm5b6o"
tenant_id = "53e8df83-c9e0-42f1-9632-91bc95e9d3c7"

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

# 🟢 查詢 OneDrive 內的檔案與資料夾
def list_drive_files(access_token):
    file_list_url = "https://graph.microsoft.com/v1.0/users/gary@kingerinc.com/drive/root/children"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(file_list_url, headers=headers)

    if response.status_code == 200:
        print("✅ OneDrive 個人檔案列表讀取成功！")
        file_list = response.json()
        
        data_folder_id = None  # 用來存 `data` 資料夾的 ID

        if "value" in file_list and len(file_list["value"]) > 0:
            print("\n📂 OneDrive 內的檔案與資料夾：")
            for item in file_list["value"]:
                if "folder" in item:
                    print(f"📁 資料夾：{item['name']} (ID: {item['id']})")
                    if item["name"].lower() == "data":  # 如果名稱是 "data"
                        data_folder_id = item["id"]
                elif "file" in item:
                    print(f"📄 檔案：{item['name']} (ID: {item['id']})")

            # 如果找到 `data` 資料夾，列出裡面的檔案
            if data_folder_id:
                print("\n📂 `data` 資料夾內的檔案：")
                list_data_folder_files(access_token, data_folder_id)
            else:
                print("\n⚠️ `data` 資料夾不存在！")
        else:
            print("⚠️ 目前 OneDrive 內沒有檔案或資料夾！")
    else:
        print(f"❌ 讀取失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")

# 🟢 查詢 `data` 資料夾內的檔案
def list_data_folder_files(access_token, folder_id):
    file_list_url = f"https://graph.microsoft.com/v1.0/users/gary@kingerinc.com/drive/items/{folder_id}/children"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(file_list_url, headers=headers)

    if response.status_code == 200:
        file_list = response.json()
        if "value" in file_list and len(file_list["value"]) > 0:
            for item in file_list["value"]:
                if "file" in item:
                    print(f"📄 檔案：{item['name']} (ID: {item['id']})")
        else:
            print("⚠️ `data` 資料夾內沒有檔案！")
    else:
        print(f"❌ 讀取 `data` 資料夾失敗，錯誤碼：{response.status_code}, 訊息：{response.text}")

# 🟢 執行流程
access_token = get_access_token()
list_drive_files(access_token)