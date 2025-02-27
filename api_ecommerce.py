import json
import subprocess
import os
from flask import Flask, request, jsonify
from database import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 讀取 config.json
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

REPO_PATH = config["repo_path"]  # 設置 repo_path VPS項目路徑
API_KEY = config.get("ecommerce_api_token")  # 讀取 API Key

def check_api_key():
    """驗證 API Key"""
    api_key = request.headers.get("Authorization")
    if not api_key or api_key != f"Bearer {API_KEY}":
        return jsonify({"error": "Invalid API Key"}), 403

# API 首頁
@app.route("/api/")
def home():
    return "Hello, api_ecommerce is running!"

# API Get VPS服務器保存代碼
@app.route("/api/get_all_files", methods=["GET"])
def get_all_files():
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    try:
        file_data = {}
        for file_name in os.listdir(REPO_PATH):
            file_path = os.path.join(REPO_PATH, file_name)
            if file_name.endswith(".py") and os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data[file_name] = f.read()
        return jsonify({"files": file_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API Get MySQL tables
@app.route('/api/get_tables', methods=['GET'])
def get_tables():
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return jsonify({"tables": tables})

# API Post Query MySQL tables
@app.route('/api/query', methods=['POST'])
def query_database():
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Missing SQL query"}), 400
    ALLOWED_KEYWORDS = ["SELECT", "FROM", "WHERE", "LIMIT", "ORDER BY", "GROUP BY"]
    if not any(keyword in query.upper() for keyword in ALLOWED_KEYWORDS):
        return jsonify({"error": "Only SELECT queries are allowed"}), 403
    if "LIMIT" not in query.upper():
        query += " LIMIT 100"
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return jsonify({"data": result})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

# GitHub Webhook: 自動拉取最新代碼
@app.route("/api/github_webhook", methods=["POST"])
def github_webhook():
    auth_error = check_api_key()
    if auth_error:
        return auth_error
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"], cwd=REPO_PATH, check=True, capture_output=True, text=True
        )
        return jsonify({"status": "✅ 更新成功", "details": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "details": e.stderr}), 500

# 服務啟動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
