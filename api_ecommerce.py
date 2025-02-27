import json
import subprocess
import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許跨域請求

# 讀取 config.json
with open("/home/ubuntu/ecommerce_analytics_db/config.json", "r") as f:
    config = json.load(f)

# 從 config.json 加載設置
REPO_PATH = config["repo_path"]
GITHUB_OWNER = "ghsu998"
GITHUB_REPO = "ecommerce_analytics_db"
GITHUB_TOKEN = config["github_token"]
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/"

# API 首頁
@app.route("/api/")
def home():
    return "Hello, api_ecommerce is running!"

# GitHub Webhook: 自動拉取最新代碼
@app.route("/api/github_webhook", methods=["POST"])
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

# API Get GitHub 最新代碼
@app.route("/api/get_all_files", methods=["GET"])
def get_all_files():
    """從 GitHub Repo 獲取最新的 .py 代碼"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)

    if response.status_code == 200:
        file_data = {}
        files = response.json()

        for file in files:
            if file["name"].endswith(".py"):  # 只獲取 .py 文件
                file_content = requests.get(file["download_url"]).text
                file_data[file["name"]] = file_content

        return jsonify({"files": file_data}), 200
    else:
        return jsonify({"error": f"GitHub API error: {response.status_code}"}), response.status_code

# 服務啟動
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
