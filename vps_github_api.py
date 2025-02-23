import os
import json
import base64
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)



# 🔹 設定 config.json 的路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # 取得目前 .py 檔案所在的資料夾
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")  # 設定 config.json 的完整路徑

@app.before_request
def redirect_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return jsonify({"error": "HTTPS only"}), 403


# 🔹 讀取 GitHub 設定
try:
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    print(f"✅ `config.json` 讀取成功！路徑: {CONFIG_PATH}")
except Exception as e:
    print(f"❌ 無法讀取 `config.json`，錯誤: {e}")
    exit(1)

# 讀取新增的 repo_path 和 script_path
GITHUB_TOKEN = config.get("github_token")
GITHUB_REPO = config.get("github_repo")
REPO_PATH = config.get("repo_path")
SCRIPT_PATH = config.get("script_path")

# 你可以將 REPO_PATH 和 SCRIPT_PATH 用於 webhook 路徑等位置



@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 只允許 GitHub Push 事件
        if request.headers.get("X-GitHub-Event") == "push":
            repo_path = "/home/ubuntu/ecommerce_analytics_db"  # ❗改成你的 Flask 目錄
            script_path = "/home/ubuntu/ecommerce_analytics_db/vps_github_api.py"  # ❗改成你的 Flask 主程式名稱

            # 拉取最新代碼
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)

            # 停止舊的 Flask 進程（如果有）
            subprocess.run(["pkill", "-f", "vps_github_api.py"])

            # 重新啟動 Flask API，並使用 nohup 讓它在背景運行
            subprocess.run(f"nohup python3 {script_path} > /dev/null 2>&1 &", shell=True)

            return jsonify({"message": "Flask API 更新完成（使用 nohup 運行）"}), 200
        else:
            return jsonify({"message": "不是 push 事件"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"message": "Flask API is running! Use /get_code?file=filename to get GitHub files."})


# 🔹 取得 GitHub 內的檔案內容
# ✅ 安全性：從 config.json 讀取 API Token
API_ACCESS_TOKEN = config.get("api_access_token")

# 讀取 config.json
with open("config.json", "r") as f:
    config = json.load(f)

GITHUB_TOKEN = config.get("github_token")
GITHUB_OWNER = config.get("github_owner")  # ✅ 確保這行有正確賦值
GITHUB_REPO = config.get("github_repo")


@app.route('/get_code', methods=['GET'])
def get_code():
    # ✅ 檢查 API Token
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

    # ✅ 錯誤處理
    if response.status_code != 200:
        return jsonify({"error": "GitHub API 回應錯誤", "details": response.json()}), response.status_code

    # 解析 JSON，並解碼 Base64 內容
    file_data = response.json()
    file_content = base64.b64decode(file_data.get("content", "")).decode("utf-8")

    # ✅ 美化輸出
    return jsonify({"file": file_path, "content": file_content})

@app.route('/list_files', methods=['GET'])
def list_files():
    repo_owner = config.get("github_owner")
    repo_name = config.get("github_repo")

    if not repo_owner or not repo_name:
        return jsonify({"error": "GitHub owner or repo name not configured"}), 400

    github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(github_api_url, headers=headers)

    if response.status_code == 200:
        file_list = [item['path'] for item in response.json()]
        return jsonify({"files": file_list}), 200
    else:
        return jsonify({"error": "Unable to fetch file list", "details": response.json()}), response.status_code


# 🔹 啟動 Flask 服務
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    print("🚀 Webhook 測試成功！")
    print(f"載入的 API_ACCESS_TOKEN: {API_ACCESS_TOKEN}")
    print(f"GITHUB_OWNER: {GITHUB_OWNER}")
    print(f"GITHUB_REPO: {GITHUB_REPO}")
    print(f"API_ACCESS_TOKEN: {API_ACCESS_TOKEN}")

