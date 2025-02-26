import json
import subprocess
import os
from flask import Flask, request, jsonify
from database import get_db_connection

app = Flask(__name__) # <---- 確保這裡的變數名稱是 `app`

# 🟢 從環境變量中讀取 GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 🔹 確保 GITHUB_TOKEN 存在
if not GITHUB_TOKEN:
    raise EnvironmentError("GitHub Token is not set in the environment variables.")

# 🟢 讀取 config.json (仍然保持 repo_path 配置)
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

REPO_PATH = config["repo_path"]  # 設置 repo_path

# 🔹 GitHub Webhook: 自動拉取最新代碼
@app.route("/github_webhook", methods=["POST"])
def github_webhook():
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"], cwd=REPO_PATH, check=True, capture_output=True, text=True
        )
        return jsonify({"status": "✅ 更新成功", "details": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "details": e.stderr}), 500

# API 首頁
@app.route("/")
def home():
    return "Hello, api_ecommerce is running!"

# API REPO_PATH
@app.route("/get_all_files", methods=["GET"])
def get_all_files():
    try:
        file_data = {}

        # 獲取 REPO_PATH 內所有 .py 檔案
        for file_name in os.listdir(REPO_PATH):
            file_path = os.path.join(REPO_PATH, file_name)

            # 只讀取 Python 檔案，確保是普通檔案
            if file_name.endswith(".py") and os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    file_data[file_name] = file_content

        # 在終端輸出所有檔案的內容
        print("\n=== 獲取的 Python 檔案內容 ===")
        for name, content in file_data.items():
            print(f"\n📂 檔案名稱: {name}")
            print("----- 內容開始 -----")
            print(content[:500])  # 只顯示前 500 個字元
            print("... (內容省略)")
            print("----- 內容結束 -----\n")

        return jsonify({"files": file_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_tables', methods=['GET'])
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return jsonify({"tables": tables})

@app.route('/get_table_data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return jsonify({"table_name": table_name, "data": data})

# 🔹 服務啟動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
