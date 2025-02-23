import os
import json
import base64
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 設定 GitHub API 相關資訊
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # ✅ 改用環境變數存儲
API_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO_PATH = os.getenv("REPO_PATH", "/home/ubuntu/ecommerce_analytics_db")
SCRIPT_PATH = os.getenv("SCRIPT_PATH", "/home/ubuntu/ecommerce_analytics_db/vps_github_api.py")

# 🔹 限制 Webhook 只接受來自 GitHub 的請求
ALLOWED_GITHUB_IPS = ["192.30.252.", "185.199.108.", "140.82.112."]

def is_github_ip(ip):
    return any(ip.startswith(prefix) for prefix in ALLOWED_GITHUB_IPS)

@app.before_request
def check_github_ip():
    if request.path == "/webhook":
        client_ip = request.remote_addr
        if not is_github_ip(client_ip):
            return jsonify({"error": "Unauthorized IP"}), 403

# 🔹 Webhook 處理：自動拉取代碼 & 重啟 Flask 服務
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("X-GitHub-Event") != "push":
        return jsonify({"message": "不是 push 事件"}), 400
    try:
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

# 🔹 取得 GitHub 內的檔案內容
@app.route('/get_code', methods=['GET'])
def get_code():
    try:
        # ✅ API Token 驗證
        client_token = request.headers.get("X-API-TOKEN")
        if not API_ACCESS_TOKEN or client_token != API_ACCESS_TOKEN:
            return jsonify({"error": "無效的 API Token"}), 403

        # 取得請求的檔案名稱
        file_path = request.args.get("file")
        if not file_path:
            return jsonify({"error": "請提供 file 參數"}), 400

        # GitHub API URL
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

        # 發送請求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 確保請求成功

        # 解析 JSON，解碼 Base64 內容
        file_data = response.json()
        file_content = base64.b64decode(file_data.get("content", "")).decode("utf-8")

        return jsonify({"file": file_path, "content": file_content})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"GitHub API 請求錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"未知錯誤: {str(e)}"}), 500

# 🔹 獲取 GitHub Repo 內的所有文件列表
@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        file_list = [item['path'] for item in response.json()]
        return jsonify({"files": file_list}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"GitHub API 請求錯誤: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"未知錯誤: {str(e)}"}), 500

# 🔹 啟動 Flask 服務
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
