import requests
import pandas as pd
import mysql.connector
import json

# ✅ 載入 config.json 設定
with open("config.json", "r") as config_file:
    config = json.load(config_file)

db_config = config["mysql"]
onedrive_config = config["onedrive"]

# ✅ 獲取 Access Token (Microsoft Graph API)
def get_access_token():
    token_url = f"https://login.microsoftonline.com/{onedrive_config['tenant_id']}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": onedrive_config["client_id"],
        "client_secret": onedrive_config["client_secret"],
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

# ✅ 連接 MySQL 並擷取 `需要補貨的 SKU`
def fetch_dvf_report():
    conn = mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )
    query = """
    SELECT SKU, Forecast_Date, Reorder_Point, Safety_Stock, 
           (FBM_Warehouse + FBA_Warehouse + Incoming_QTY) AS Available_Stock,
           DVF_Quantity
    FROM kin_sku_DVF_history_weekly
    WHERE DVF_Quantity > 0  -- 只取需要補貨的 SKU
    ORDER BY DVF_Quantity DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ✅ 將 DataFrame 轉為 HTML 表格
def format_email_content(df):
    if df.empty:
        return "<h2>🎉 今天沒有需要補貨的 SKU！</h2>"

    html_table = df.to_html(index=False, border=1, justify="center")
    return f"""
    <html>
    <body>
        <h2>📌 Daily DVF Report - 需要補貨的 SKU</h2>
        <p>以下是今天需要補貨的 SKU：</p>
        {html_table}
        <p>📌 本報表由系統自動生成</p>
    </body>
    </html>
    """

# ✅ 使用 Microsoft Graph API 發送 Email
def send_email(report_html):
    access_token = get_access_token()  # 獲取 OAuth Token
    email_url = f"https://graph.microsoft.com/v1.0/users/{onedrive_config['email_sender']}/sendMail"
    
    email_data = {
        "message": {
            "subject": "📌 Daily DVF Report - 需要補貨的 SKU",
            "body": {
                "contentType": "HTML",
                "content": report_html
            },
            "toRecipients": [
                {"emailAddress": {"address": onedrive_config["email_receiver"]}}
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(email_url, json=email_data, headers=headers)

    if response.status_code == 202:
        print("✅ Email 報表發送成功！")
    else:
        print(f"❌ Email 發送失敗，錯誤碼: {response.status_code}, 訊息: {response.text}")

# ✅ 執行流程
def main():
    df = fetch_dvf_report()
    email_content = format_email_content(df)
    send_email(email_content)

# 🚀 執行主程式
if __name__ == "__main__":
    main()