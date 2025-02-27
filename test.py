import requests

url = "https://ecommerce.taigers.com/api/get_all_files"

# 如果 API 需要 Token，請加上 Authorization 標頭
headers = {
    "Authorization": "Bearer YOUR_API_KEY"  # 如果不需要身份驗證，可以省略這一行
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 如果發生 HTTP 錯誤，會拋出異常
    print("✅ API Response:", response.json())  # 以 JSON 形式打印回應
except requests.exceptions.RequestException as e:
    print("❌ Error:", e)



import secrets
api_key = secrets.token_hex(32)  # 生成 64 字元（32 byte）隨機 API Key
print(api_key)