import os
import json
import base64
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 讀取 `config.json`
CONFIG_PATH = "/home/ubuntu/ecommerce_analytics_db/config.json"

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

config = load_config()

# 🔹 設定 GitHub API 相關資訊
GITHUB_TOKEN = config["github_token"]
API_ACCESS_TOKEN = config["api_access_token"]
GITHUB_OWNER = config["github_owner"]
GITHUB_REPO = config["github_repo"]
REPO_PATH = config["repo_path"]
SCRIPT_PATH = config["script_path"]

# 🔹 Webhook 處理：自動拉取代碼 & 重啟 Flask 服務
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("X-GitHub-Event") != "push":
        return jsonify({"message": "不是 push 事件"}), 400
    try:
        # 重新載入 config.json（確保最新設定）
        global config, GITHUB_TOKEN, API_ACCESS_TOKEN
        config = load_config()
        GITHUB_TOKEN = config["github_token"]
        API_ACCESS_TOKEN = config["api_access_token"]

        # 拉取最新代碼
        subprocess.run(["git", "-C", REPO_PATH, "pull"], check=True)

        # 重啟 Flask API (使用 systemd)
        subprocess.run(["sudo", "systemctl", "restart", "flask_api"], check=True)

        return jsonify({"message": "Flask API 已更新並重新啟動"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 測試 API 是否運行
@app.route("/")
def home():
    return jsonify({"message": "Flask API is running! Use /get_code?file=filename to get GitHub files."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
