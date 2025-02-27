import json
import subprocess
import os
import requests
from flask import Flask, request, jsonify
from database import get_db_connection
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許跨域請求

# 讀取 config.json
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

REPO_PATH = config["repo_path"]  # VPS 項目路徑
API_KEY = config.get("ecommerce_api_token")  # API Key

# GitHub 配置
GITHUB_OWNER = config["github_owner"]
GITHUB_REPO = config["github_repo"]
GITHUB_TOKEN = config["github_token"]
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"

# API Token 驗證裝飾器
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if not api_key or not api_key.startswith("Bearer ") or api_key.split("Bearer ")[-1] != API_KEY:
            return jsonify({"error": "Invalid API Key"}), 403
        return f(*args, **kwargs)
    return decorated_function

# API 首頁
@app.route("/api/")
def home():
    return "Hello, api_ecommerce is running!"

# API Get GitHub 最新代碼
@app.route("/api/get_all_files", methods=["GET"])
@require_api_key
def get_all_files():
    """從 GitHub Repo 獲取最新的 .py 代碼"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        file_data = {}
        files = response.json()

        for file in files:
            if file["name"].endswith(".py"):  # 只獲取 .py 文件
                file_url = file["download_url"]
                try:
                    file_content = requests.get(file_url).text
                    file_data[file["name"]] = file_content
                except Exception as e:
                    file_data[file["name"]] = f"Error fetching file: {str(e)}"

        return jsonify({"files": file_data}), 200
    elif response.status_code == 403:  # GitHub API 限流
        return jsonify({"error": "GitHub API rate limit exceeded. Try again later."}), 429
    else:
        return jsonify({"error": f"GitHub API error: {response.status_code}"}), 500

# API Get MySQL tables
@app.route('/api/get_tables', methods=['GET'])
@require_api_key
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return jsonify({"tables": tables})

# API Post Query MySQL tables
@app.route('/api/query', methods=['POST'])
@require_api_key
def query_database():
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
@require_api_key
def github_webhook():
    """觸發 GitHub Webhook 自動同步代碼"""
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
        return jsonify({"status": "✅ 更新成功", "details": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Git pull failed", "details": e.stderr}), 500

# 服務啟動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
